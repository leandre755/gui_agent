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

### Step 7: Corriger les constats Greptile sur le commit local
- [x] **Action**: Traiter les trois constats P1 : alias d'ancre bloc résolu à vide, collection flow ancrée multilignes interrompue avant fermeture, et `concurrency:` vide accepté sans groupe.
- [x] **Verify**: `./venv/bin/pytest -q tests/test_verify_workflows.py -k 'block_anchored_trigger_alias or multiline_anchored_trigger_mapping or empty_concurrency_for_push or anchored_trigger_mapping or inline_anchored_trigger_values'` puis `./ci.sh`
- **Verification Proof**:
```text
Greptile local sur commit 6976b3a : Confidence 0/5, 2 constats P1 sécurité et 1 défaut concurrency.
RED : alias bloc, mapping multiline et concurrency vide reproduits à 0 erreur.
GREEN ciblé : 5 passed, 12 deselected.
CI finale : 6 étapes PASS, 44/44 tests, workflows 6/6 conformes.
Aucun push effectué.
```

### Step 8: Corriger les constats Greptile sur les alias externes et l'ordre concurrency
- [x] **Action**: Résoudre les ancres flow multilignes et séquences bloc externes référencées par alias, et parcourir tous les enfants de `concurrency:` pour accepter un `group` valide quel que soit son ordre.
- [x] **Verify**: `./venv/bin/pytest -q tests/test_verify_workflows.py -k 'external_multiline_and_sequence_anchor_aliases or accept_concurrency_group_after_cancel_in_progress or block_anchored_trigger_alias or multiline_anchored_trigger_mapping or empty_concurrency_for_push or anchored_trigger_mapping or inline_anchored_trigger_values'` puis `./ci.sh`
- **Verification Proof**:
```text
Greptile local sur commit 1894b95 : Confidence 2/5, 2 constats P1.
RED : alias flow/séquence externes et group après cancel-in-progress reproduits.
GREEN ciblé : 7 passed, 12 deselected.
CI finale : 6 étapes PASS, 46/46 tests, workflows 6/6 conformes.
Aucun push effectué.
```

### Step 9: Commit local et nouvelle revue Greptile sans push
- [ ] **Action**: Créer un troisième commit local avec le correctif et exécuter une seule revue Greptile contre `main`; ne pas pousser.
- [ ] **Verify**: Greptile doit atteindre 5/5 sans finding P1/P2, puis lire le résultat complet avant toute action distante.
- **Verification Proof**:
```text
En attente du troisième commit local et de la revue Greptile.
```
