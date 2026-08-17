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


def test_nested_escaped_event_keys_and_dispatch_inputs_not_confused(tmp_path: Path):
    """Vérifie que les clés d'événements échappées (ex: 'pull_request_t\\u0061rget') sont bien détectées, et que le texte des inputs workflow_dispatch n'est pas confondu avec un trigger."""
    # 1. Échappement imbriqué de pull_request_target
    wf_escaped = tmp_path / "nested_escaped_trigger.yml"
    wf_escaped.write_text(
        """
name: Nested Escaped PR Target
on:
  "pull_request_t\\u0061rget":
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
      - run: echo test
""",
        encoding="utf-8",
    )
    count1, errors1, _ = verify_workflows.check_workflow(wf_escaped)
    assert count1 >= 1
    assert any("pull_request_target est formellement interdit" in e for e in errors1)

    # 2. workflow_dispatch avec descriptions ou valeurs contenant 'push' ou 'pull_request'
    wf_inputs = tmp_path / "dispatch_with_input_text.yml"
    wf_inputs.write_text(
        """
name: Dispatch Inputs
on:
  workflow_dispatch:
    inputs:
      action_type:
        description: "Trigger a push or pull_request deployment"
        default: "push"
        required: true
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count2, errors2, _ = verify_workflows.check_workflow(wf_inputs)
    assert count2 == 0, f"Erreurs inattendues pour inputs de workflow_dispatch: {errors2}"


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


def test_accept_runs_on_mapping_and_trailing_whitespace_timeout(tmp_path: Path):
    """Vérifie que runs-on sous forme de mapping et timeout-minutes avec espaces de fin sont acceptés."""
    wf = tmp_path / "mapping_runner_trailing_timeout.yml"
    wf.write_text(
        """
name: Mapping Runner
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  mapping_job:
    runs-on:
      group: ubuntu-runners
      labels: [ubuntu-latest, gpu]
    timeout-minutes: 10
    steps:
      - run: echo success
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count == 0, f"Erreurs inattendues: {errors}"


def test_accept_indentationless_runs_on_sequence_and_yaml_aliases(tmp_path: Path):
    """Vérifie que les séquences runs-on sans indentation supplémentaire et les alias YAML pour on: sont correctement acceptés/résolus."""
    # 1. runs-on avec séquence sans indentation supplémentaire
    wf_runner = tmp_path / "indentationless_runner.yml"
    wf_runner.write_text(
        """
name: Indentationless Runner
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  test:
    runs-on:
    - self-hosted
    - linux
    timeout-minutes: 5
    steps:
      - run: echo success
""",
        encoding="utf-8",
    )
    count1, errors1, _ = verify_workflows.check_workflow(wf_runner)
    assert count1 == 0, f"Erreurs inattendues pour runner sans indentation: {errors1}"

    # 2. on: avec alias YAML vers pull_request_target
    wf_alias = tmp_path / "alias_pr_target.yml"
    wf_alias.write_text(
        """
name: Alias PR Target
unsafe_events: &unsafe [pull_request_target]
on: *unsafe
permissions:
  contents: read
concurrency:
  group: test-${{ github.ref }}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count2, errors2, _ = verify_workflows.check_workflow(wf_alias)
    assert count2 >= 1
    assert any("pull_request_target est formellement interdit" in e for e in errors2)


def test_reject_block_anchored_trigger_alias(tmp_path: Path):
    wf = tmp_path / "block_anchor_alias.yml"
    wf.write_text(
        """
name: Block Anchor Alias
events: &events
  pull_request_target:
    types: [opened]
on: *events
permissions:
  contents: read
concurrency:
  group: test-${{ github.ref }}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 1
    assert any("pull_request_target est formellement interdit" in e for e in errors)


def test_reject_external_multiline_and_sequence_anchor_aliases(tmp_path: Path):
    multiline_flow = tmp_path / "external_multiline_flow_anchor.yml"
    multiline_flow.write_text(
        """
name: External Multiline Flow Anchor
events: &events {
  pull_request_target: null
}
on: *events
permissions:
  contents: read
concurrency:
  group: test-${{ github.ref }}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count1, errors1, _ = verify_workflows.check_workflow(multiline_flow)
    assert count1 >= 1
    assert any("pull_request_target est formellement interdit" in e for e in errors1)

    block_sequence = tmp_path / "external_block_sequence_anchor.yml"
    block_sequence.write_text(
        """
name: External Block Sequence Anchor
events: &events
  - pull_request_target
on: *events
permissions:
  contents: read
concurrency:
  group: test-${{ github.ref }}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count2, errors2, _ = verify_workflows.check_workflow(block_sequence)
    assert count2 >= 1
    assert any("pull_request_target est formellement interdit" in e for e in errors2)


def test_reject_external_multiline_flow_sequence_anchor_alias(tmp_path: Path):
    wf = tmp_path / "external_multiline_flow_sequence_anchor.yml"
    wf.write_text(
        """
name: External Multiline Flow Sequence Anchor
events: &events [
  pull_request_target
]
on: *events
permissions:
  contents: read
concurrency:
  group: test-${{ github.ref }}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 1
    assert any("pull_request_target est formellement interdit" in e for e in errors)


def test_accept_concurrency_group_after_cancel_in_progress(tmp_path: Path):
    wf = tmp_path / "concurrency_group_after_cancel.yml"
    wf.write_text(
        """
name: Concurrency Group Order
on: push
permissions:
  contents: read
concurrency:
  cancel-in-progress: true
  group: test-${{ github.ref }}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count == 0, f"Erreurs inattendues: {errors}"


def test_reject_scalar_trigger_anchor_aliases(tmp_path: Path):
    scalar_pr_target = tmp_path / "scalar_pr_target_anchor.yml"
    scalar_pr_target.write_text(
        """
name: Scalar PR Target Anchor
events: &events pull_request_target
on: *events
permissions:
  contents: read
concurrency:
  group: test-${{ github.ref }}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count1, errors1, _ = verify_workflows.check_workflow(scalar_pr_target)
    assert count1 >= 1
    assert any("pull_request_target est formellement interdit" in e for e in errors1)

    scalar_push = tmp_path / "scalar_push_anchor.yml"
    scalar_push.write_text(
        """
name: Scalar Push Anchor
events: &events push
on: *events
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count2, errors2, _ = verify_workflows.check_workflow(scalar_push)
    assert count2 >= 1
    assert any("concurrency" in e for e in errors2)


def test_reject_multiline_flow_concurrency_without_group(tmp_path: Path):
    wf = tmp_path / "multiline_flow_concurrency_without_group.yml"
    wf.write_text(
        """
name: Multiline Flow Concurrency
on: push
permissions:
  contents: read
concurrency: {
  cancel-in-progress: true
}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 1
    assert any("concurrency" in e for e in errors)


def test_reject_multiline_anchored_trigger_mapping(tmp_path: Path):
    wf = tmp_path / "multiline_anchor_mapping.yml"
    wf.write_text(
        """
name: Multiline Anchor Mapping
on: &events {
  pull_request_target: null
}
permissions:
  contents: read
concurrency:
  group: test-${{ github.ref }}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 1
    assert any("pull_request_target est formellement interdit" in e for e in errors)


def test_reject_anchored_trigger_mapping_and_require_concurrency(tmp_path: Path):
    anchored_pr_target = tmp_path / "anchored_pr_target.yml"
    anchored_pr_target.write_text(
        """
name: Anchored PR Target
on: &events
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
      - run: echo test
""",
        encoding="utf-8",
    )
    count1, errors1, _ = verify_workflows.check_workflow(anchored_pr_target)
    assert count1 >= 1
    assert any("pull_request_target est formellement interdit" in e for e in errors1)

    anchored_push = tmp_path / "anchored_push.yml"
    anchored_push.write_text(
        """
name: Anchored Push
on: &events
  push:
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count2, errors2, _ = verify_workflows.check_workflow(anchored_push)
    assert count2 >= 1
    assert any("Bloc top-level 'concurrency:' manquant" in e for e in errors2)


def test_reject_empty_concurrency_for_push(tmp_path: Path):
    wf = tmp_path / "empty_concurrency.yml"
    wf.write_text(
        """
name: Empty Concurrency
on: push
permissions:
  contents: read
concurrency:
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count >= 1
    assert any("concurrency" in e for e in errors)


def test_reject_inline_anchored_trigger_values(tmp_path: Path):
    anchored_pr_target = tmp_path / "inline_anchored_pr_target.yml"
    anchored_pr_target.write_text(
        """
name: Inline Anchored PR Target
on: &events [pull_request_target]
permissions:
  contents: read
concurrency:
  group: test-${{ github.ref }}
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count1, errors1, _ = verify_workflows.check_workflow(anchored_pr_target)
    assert count1 >= 1
    assert any("pull_request_target est formellement interdit" in e for e in errors1)

    anchored_push = tmp_path / "inline_anchored_push.yml"
    anchored_push.write_text(
        """
name: Inline Anchored Push
on: &events [push]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo test
""",
        encoding="utf-8",
    )
    count2, errors2, _ = verify_workflows.check_workflow(anchored_push)
    assert count2 >= 1
    assert any("Bloc top-level 'concurrency:' manquant" in e for e in errors2)


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


def test_accept_alternate_yaml_indentation(tmp_path: Path):
    """Vérifie que les workflows avec indentation variable (ex: 4 espaces pour jobs, 8 espaces pour properties) sont supportés."""
    wf = tmp_path / "alternate_indent.yml"
    wf.write_text(
        """
name: Alternate Indent
on:
    workflow_dispatch:
permissions:
    contents: read
jobs:
    build_and_test:
        runs-on: ubuntu-22.04
        timeout-minutes: 15
        steps:
            - run: echo success
""",
        encoding="utf-8",
    )
    count, errors, _ = verify_workflows.check_workflow(wf)
    assert count == 0, f"Erreurs inattendues pour indentation alternative: {errors}"


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
