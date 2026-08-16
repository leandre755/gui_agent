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
    """Valide que les 6 workflows réels du dépôt respectent 100% des invariants."""
    workflows_dir = Path(__file__).resolve().parent.parent / ".github" / "workflows"
    workflows = sorted([*workflows_dir.glob("*.yml"), *workflows_dir.glob("*.yaml")])
    assert len(workflows) == 6, f"Attendu 6 workflows, trouvé {len(workflows)}"

    for wf_path in workflows:
        errors_count, errors, _warnings = verify_workflows.check_workflow(wf_path)
        assert errors_count == 0, f"Erreurs trouvées dans {wf_path}: {errors}"


def test_reject_pull_request_target(tmp_path: Path):
    """Vérifie le rejet strict du déclencheur pull_request_target."""
    wf = tmp_path / "bad_pr_target.yml"
    wf.write_text(
        """
name: Insecure PR Target
on:
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


def test_reject_write_all_permissions(tmp_path: Path):
    """Vérifie le rejet strict de permissions: write-all."""
    wf = tmp_path / "write_all.yml"
    wf.write_text(
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
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 1
    assert any("write-all' est strictement interdite" in e for e in errors)


def test_reject_missing_timeout_or_runs_on(tmp_path: Path):
    """Vérifie l'obligation des clés runs-on et timeout-minutes par job."""
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
      - run: echo hello
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 2
    assert any("runs-on:' obligatoire manquante" in e for e in errors)
    assert any("timeout-minutes:' obligatoire manquante" in e for e in errors)


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


def test_reject_missing_concurrency_on_pr_push(tmp_path: Path):
    """Vérifie l'obligation de la clé concurrency pour les workflows déclenchés par push/PR."""
    wf = tmp_path / "missing_concurrency.yml"
    wf.write_text(
        """
name: Missing Concurrency
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
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 1
    assert any("Bloc top-level 'concurrency:' manquant" in e for e in errors)
