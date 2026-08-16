# Execution Plan: Validation Métier et Invariants de Sécurité des Workflows GitHub Actions (Issue #26)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: `.github/scripts/verify_workflows.py` vérifie de manière exhaustive les invariants structurels et de sécurité des workflows GitHub Actions (sans dépendance externe, stdlib Python uniquement) : permissions least-privilege, timeout-minutes par job, runs-on, persist-credentials: false, interdiction de pull_request_target et write-all, SHA de 40 caractères immuable pour les actions tierces, et conformité de la concurrence (y compris flow-style et clés entre guillemets).
- **Pre-requisites**: 6 workflows GitHub Actions conformes dans `.github/workflows/`, suite de tests pytest et exécution intégrée dans `ci.sh`.

## 🛠️ Step-by-Step Sequence

### Step 1: Enrichir `.github/scripts/verify_workflows.py` avec validation structurelle et métier
- [x] **Action**: Implémenter dans `.github/scripts/verify_workflows.py` les vérifications complètes des invariants de sécurité et structurels (support des clés avec guillemets, concurrency scalaire/flow-style, parsing dynamique de l'indentation YAML des jobs).
- [x] **Verify**: `python3 .github/scripts/verify_workflows.py .github/workflows`
- **Verification Proof**:
```text
Validation réussie : 6 workflow(s) GitHub Actions conformes.
```

### Step 2: Ajouter la suite de tests unitaires dédiée `tests/test_verify_workflows.py`
- [x] **Action**: Créer `tests/test_verify_workflows.py` couvrant les scénarios d'invariants et de cas limites (indentation variable, faux positifs scripts imbriqués).
- [x] **Verify**: `uv run --with pytest pytest -v tests/test_verify_workflows.py`
- **Verification Proof**:
```text
============================== 37 passed in 9.72s ==============================
```

### Step 3: Intégrer la validation des workflows dans la CI locale `ci.sh`
- [x] **Action**: Ajouter l'étape 2 "Validation Workflows GitHub Actions" dans `ci.sh` et mettre à jour l'aide `--quick`.
- [x] **Verify**: `./ci.sh`
- **Verification Proof**:
```text
| Compilation Bytecode Python (compileall)   | PASS       | 180ms      |
| Validation Workflows GitHub Actions        | PASS       | 50ms       |
| Linter de Code (Ruff Check)                | PASS       | 62ms       |
| Formatage de Code (Ruff Format)            | PASS       | 64ms       |
| Typage Statique Strict (Mypy)              | PASS       | 511ms      |
| Suite de Tests Pytest                      | PASS       | 10947ms    |
🎉 Toutes les étapes CI sont validées avec succès !
```

### Step 4: Exécuter les boucles de revue Greptile et Optibot jusqu'à 5/5
- [x] **Action**: Itérer sur les retours Greptile / Optibot jusqu'à l'obtention du score parfait 5/5 et 0 commentaire non résolu.
- [x] **Verify**: `greptile review show` & GraphQL `reviewThreads`
- **Verification Proof**:
```text
Greptile Summary:
Confidence: 5/5
The PR appears safe to merge.
No blocking failure remains.
No review comments.
Unresolved review threads: 0
```
