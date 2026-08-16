# Execution Plan: Validation Métier et Invariants de Sécurité des Workflows GitHub Actions (Issue #26)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: `.github/scripts/verify_workflows.py` vérifie de manière exhaustive les invariants structurels et de sécurité des workflows GitHub Actions (sans dépendance externe, stdlib Python uniquement) : permissions least-privilege, timeout-minutes par job, runs-on, persist-credentials: false, interdiction de pull_request_target et write-all, SHA de 40 caractères immuable pour les actions tierces, et conformité de la concurrence.
- **Pre-requisites**: 6 workflows GitHub Actions conformes dans `.github/workflows/`, suite de tests pytest et exécution intégrée dans `ci.sh`.

## 🛠️ Step-by-Step Sequence

### Step 1: Enrichir `.github/scripts/verify_workflows.py` avec validation structurelle et métier
- [x] **Action**: Implémenter dans `.github/scripts/verify_workflows.py` les vérifications complètes des invariants de sécurité et structurels.
- [x] **Verify**: `python3 .github/scripts/verify_workflows.py .github/workflows`
- **Verification Proof**:
```text
Validation réussie : 6 workflow(s) GitHub Actions conformes.
```

### Step 2: Ajouter la suite de tests unitaires dédiée `tests/test_verify_workflows.py`
- [x] **Action**: Créer `tests/test_verify_workflows.py` couvrant les 8 scénarios d'invariants.
- [x] **Verify**: `uv run --with pytest pytest -v tests/test_verify_workflows.py`
- **Verification Proof**:
```text
tests/test_verify_workflows.py::test_existing_workflows_are_all_valid PASSED [ 12%]
tests/test_verify_workflows.py::test_reject_pull_request_target PASSED   [ 25%]
tests/test_verify_workflows.py::test_reject_missing_top_level_permissions PASSED [ 37%]
tests/test_verify_workflows.py::test_reject_write_all_permissions PASSED [ 50%]
tests/test_verify_workflows.py::test_reject_missing_timeout_or_runs_on PASSED [ 62%]
tests/test_verify_workflows.py::test_reject_unpinned_action_ref PASSED   [ 75%]
tests/test_verify_workflows.py::test_reject_persist_credentials_true PASSED [ 87%]
tests/test_verify_workflows.py::test_reject_missing_concurrency_on_pr_push PASSED [100%]
8 passed in 0.06s
```

### Step 3: Intégrer la validation des workflows dans la CI locale `ci.sh`
- [x] **Action**: Ajouter l'étape 2 "Validation Workflows GitHub Actions" dans `ci.sh`.
- [x] **Verify**: `./ci.sh`
- **Verification Proof**:
```text
| Compilation Bytecode Python (compileall)   | PASS       | 116ms      |
| Validation Workflows GitHub Actions        | PASS       | 44ms       |
| Linter de Code (Ruff Check)                | PASS       | 42ms       |
| Formatage de Code (Ruff Format)            | PASS       | 40ms       |
| Typage Statique Strict (Mypy)              | PASS       | 313ms      |
| Suite de Tests Pytest                      | PASS       | 8309ms     |
🎉 Toutes les étapes CI sont validées avec succès !
```

### Step 4: Exécuter la suite complète de validation qualité et ouvrir la PR
- [ ] **Action**: Valider compilation, Ruff check, Ruff format, Mypy, Pytest (100% PASS).
- [ ] **Verify**: `./ci.sh` et `git status`
- **Verification Proof**:
```text
[Output will be inserted here]
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Faux positifs lors de l'analyse textuelle/YAML de workflows complexes (blocs multiline, expressions GitHub context ${{ ... }}).
- **Mitigation**: Implémenter un analyseur ligne par ligne structuré par état (gestion des sections `jobs:`, `permissions:`, `steps:`, `uses:`, etc.) avec tolérance pour les expressions dynamiques mais contrôle strict des clés de configuration.
