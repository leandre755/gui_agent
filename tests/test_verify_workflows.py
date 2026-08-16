"""Tests unitaires pour .github/scripts/verify_workflows.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

# Chargement dynamique du script verify_workflows.py sans dépendre du sys.path
SCRIPT_PATH = Path(__file__).resolve().parent.parent / ".github" / "scripts" / "verify_workflows.py"
spec = importlib.util.spec_from_file_location("verify_workflows", str(SCRIPT_PATH))
assert spec is not None and spec.loader is not None
verify_workflows: Any = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_workflows)


def test_existing_workflows_are_all_valid():
    """Valide que tous les workflows réels du dépôt respectent 100% des invariants."""
    workflows_dir = Path(__file__).resolve().parent.parent / ".github" / "workflows"
    workflows = sorted([*workflows_dir.glob("*.yml"), *workflows_dir.glob("*.yaml")])
    assert len(workflows) > 0, "Aucun workflow trouvé dans .github/workflows"

    for wf_path in workflows:
        errors_count, errors, _warnings = verify_workflows.check_workflow(wf_path)
        assert errors_count == 0, f"Erreurs trouvées dans {wf_path}: {errors}"


def test_reject_pull_request_target(tmp_path: Path):
    """Vérifie le rejet strict du déclencheur pull_request_target même sous clé avec guillemets."""
    wf = tmp_path / "bad_pr_target.yml"
    wf.write_text(
        """
name: Insecure PR Target
"on":
  pull_request_target:
    types: [opened]
permissions:
  contents: read
concurrency:
  group: test-${{ github.ref }}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v4.4.2
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 1
    assert any("pull_request_target est formellement interdit" in e for e in errors)


def test_reject_missing_top_level_permissions(tmp_path: Path):
    """Vérifie le rejet en l'absence de bloc permissions top-level."""
    wf = tmp_path / "missing_perms.yml"
    wf.write_text(
        """
name: Missing Perms
on:
  workflow_dispatch:
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo hello
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 1
    assert any("Bloc top-level 'permissions:' manquant" in e for e in errors)


def test_reject_write_all_and_write_permissions(tmp_path: Path):
    """Vérifie le rejet strict de permissions: write-all et permissions: write."""
    wf1 = tmp_path / "write_all.yml"
    wf1.write_text(
        """
name: Write All Perms
on:
  workflow_dispatch:
permissions: write-all
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo hello
""",
        encoding="utf-8",
    )
    count1, errors1, _ = verify_workflows.check_workflow(wf1)
    assert count1 >= 1
    assert any("write-all" in e for e in errors1)

    wf2 = tmp_path / "write_scalar.yml"
    wf2.write_text(
        """
name: Write Scalar Perms
on:
  workflow_dispatch:
permissions: write
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo hello
""",
        encoding="utf-8",
    )
    count2, errors2, _ = verify_workflows.check_workflow(wf2)
    assert count2 >= 1
    assert any("write" in e for e in errors2)


def test_reject_missing_timeout_or_runs_on_and_no_nested_leak(tmp_path: Path):
    """Vérifie que les clés runs-on et timeout-minutes doivent être au niveau du job et non dans un script imbriqué."""
    wf = tmp_path / "missing_job_keys.yml"
    wf.write_text(
        """
name: Incomplete Job
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  incomplete_job:
    steps:
      - name: Nested fake step
        run: |
          echo "runs-on: ubuntu-latest"
          echo "timeout-minutes: 5"
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 2
    assert any("runs-on:' obligatoire manquante" in e for e in errors)
    assert any("timeout-minutes:' obligatoire manquante" in e for e in errors)


def test_accept_matrix_runs_on_and_commented_timeout(tmp_path: Path):
    """Vérifie que les expressions runs-on et les commentaires inline sur timeout-minutes sont acceptés."""
    wf = tmp_path / "dynamic_job.yml"
    wf.write_text(
        """
name: Dynamic Job
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  dynamic_job:
    runs-on: ${{ matrix.os }}
    timeout-minutes: 10 # 10 minutes cap
    steps:
      - run: echo hello
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count == 0, f"Erreurs inattendues: {errors}"


def test_reject_unpinned_action_ref(tmp_path: Path):
    """Vérifie le rejet des actions non épinglées par SHA-40."""
    wf = tmp_path / "unpinned_action.yml"
    wf.write_text(
        """
name: Unpinned Action
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 1
    assert any("SHA complet de 40 caractères" in e for e in errors)


def test_reject_persist_credentials_true(tmp_path: Path):
    """Vérifie le rejet de persist-credentials: true."""
    wf = tmp_path / "persist_creds.yml"
    wf.write_text(
        """
name: Persist Credentials
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v4.4.2
        with:
          persist-credentials: true
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 1
    assert any("persist-credentials: true est formellement interdit" in e for e in errors)


def test_accept_scalar_concurrency(tmp_path: Path):
    """Vérifie que la syntaxe scalaire de concurrency est bien reconnue."""
    wf = tmp_path / "scalar_concurrency.yml"
    wf.write_text(
        """
name: Scalar Concurrency
on:
  pull_request:
permissions:
  contents: read
concurrency: build-${{ github.ref }}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo hello
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count == 0, f"Erreurs inattendues: {errors}"


def test_reject_missing_concurrency_flow_style_and_mapping(tmp_path: Path):
    """Vérifie l'obligation de concurrency pour les déclencheurs mapping et flow-style list."""
    wf_mapping = tmp_path / "missing_concurrency_mapping.yml"
    wf_mapping.write_text(
        """
name: Missing Concurrency Mapping
on:
  pull_request:
    branches: [main]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo hello
""",
        encoding="utf-8",
    )
    count1, errors1, _ = verify_workflows.check_workflow(wf_mapping)
    assert count1 >= 1
    assert any("Bloc top-level 'concurrency:' manquant" in e for e in errors1)

    wf_flow = tmp_path / "missing_concurrency_flow.yml"
    wf_flow.write_text(
        """
name: Missing Concurrency Flow
on: [push, pull_request]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo hello
""",
        encoding="utf-8",
    )
    count2, errors2, _ = verify_workflows.check_workflow(wf_flow)
    assert count2 >= 1
    assert any("Bloc top-level 'concurrency:' manquant" in e for e in errors2)
