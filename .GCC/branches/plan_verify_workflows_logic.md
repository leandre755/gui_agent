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

### Step 4: Lire le verdict réel de la PR #36 et identifier le blocage
- [x] **Action**: Lire la description, le résumé Greptile le plus récent, le bilan CodeRabbit, le bilan Optibot et tous les commentaires/threads de la PR #36 avant toute nouvelle relance.
- [x] **Verify**: `gh pr view 36 --repo leandre755/gui_agent --json body,comments,reviews,latestReviews` et GraphQL `reviewThreads`
- **Verification Proof**:
```text
Greptile Summary: Confidence Score: 3/5
One security-relevant blocking failure remains in .github/scripts/verify_workflows.py.
Anchored trigger declarations using `on: &events` bypass pull_request_target and concurrency validation.
Unresolved Greptile thread: .github/scripts/verify_workflows.py:210
Optibot latest status: Code Looks Good; no blocking issues found.
CodeRabbit latest explicit review request: rate limited; no fresh verdict available.
```

### Step 5: Corriger le contournement des triggers ancrés
- [x] **Action**: Traiter une valeur top-level `on: &events` comme une métadonnée YAML et poursuivre l'analyse du mapping enfant dans `.github/scripts/verify_workflows.py`; ajouter une régression pour `pull_request_target` et `push` sans `concurrency`.
- [x] **Verify**: `./venv/bin/pytest -q tests/test_verify_workflows.py -k anchored_trigger_mapping`
- **Verification Proof**:
```text
RED (avant correctif): 1 failed, 12 deselected in 0.18s
GREEN (après correctif): 1 passed, 12 deselected in 0.04s
```

### Step 6: Corriger les valeurs d'ancre inline signalées par CodeRabbit
- [x] **Action**: Gérer `on: &events [pull_request_target]` et `on: &events [push]` en analysant la collection inline après l'ancre, tout en conservant l'analyse du mapping enfant pour une ancre seule.
- [x] **Verify**: `./venv/bin/pytest -q tests/test_verify_workflows.py -k 'anchored_trigger_mapping or inline_anchored_trigger_values'`
- **Verification Proof**:
```text
CodeRabbit local : 1 finding major sur le suffixe inline de l'ancre.
RED (avant correctif): 1 failed, 13 deselected
GREEN (après correctif): 2 passed, 12 deselected
```

### Step 7: Validation locale obligatoire avant push et relecture du verdict distant
- [x] **Action**: Exécuter séquentiellement `./ci.sh`, les tests ciblés, `greptile review --agent --branch main`, `coderabbit review --agent --uncommitted --base main` et vérifier TestSprite si son agent est configuré. Ne pousser qu'après zéro problème actionnable local.
- [ ] **Verify**: Lire après push la description PR, le résumé Greptile, le bilan CodeRabbit, le bilan Optibot et 100 % des commentaires/threads; atteindre Greptile 5/5, zéro échec de sécurité, zéro commentaire actionnable et zéro blocage.
- **Verification Proof**:
```text
./ci.sh : 6 étapes PASS, 41/41 tests.
CodeRabbit local : review_completed, findings: 0, reviewedFiles: .github/scripts/verify_workflows.py.
Greptile local : review lancé avec --branch main, mais 8 fichiers non committés ignorés ; résultat 2/5 sur HEAD 1ce6e31, donc non valable pour le correctif actuel.
TestSprite : CLI disponible et authentifié, agent de vérification non installé ; aucun test distant déclenché.
Aucun push effectué.
```
