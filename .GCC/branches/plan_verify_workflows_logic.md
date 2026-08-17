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

### Step 9: Corriger le P1 sur les séquences flow multilignes externes
- [x] **Action**: Préserver le délimiteur flow inline (`[`) de l'ancre externe lors de la reconstruction de ses lignes enfants afin de résoudre correctement `on: *events`.
- [x] **Verify**: `./venv/bin/pytest -q tests/test_verify_workflows.py -k 'external_multiline_flow_sequence_anchor_alias or external_multiline_and_sequence_anchor_aliases or accept_concurrency_group_after_cancel_in_progress or block_anchored_trigger_alias or multiline_anchored_trigger_mapping or empty_concurrency_for_push or anchored_trigger_mapping or inline_anchored_trigger_values'` puis `./ci.sh`
- **Verification Proof**:
```text
Greptile local sur commit 637e516 : Confidence 3/5, 1 constat P1.
RED : séquence flow externe multiline reproduite à 0 erreur.
GREEN ciblé : 8 passed, 12 deselected.
CI finale : 6 étapes PASS, 47/47 tests, workflows 6/6 conformes.
Aucun push effectué.
```

### Step 10: Corriger le P1 sur les ancres scalaires externes
- [x] **Action**: Enregistrer les valeurs scalaires non vides des ancres externes afin que les alias `on: *events` conservent les triggers `pull_request_target`, `push` et `pull_request`.
- [x] **Verify**: `./venv/bin/pytest -q tests/test_verify_workflows.py -k 'scalar_trigger_anchor_aliases or external_multiline_flow_sequence_anchor_alias or external_multiline_and_sequence_anchor_aliases or accept_concurrency_group_after_cancel_in_progress or block_anchored_trigger_alias or multiline_anchored_trigger_mapping or empty_concurrency_for_push or anchored_trigger_mapping or inline_anchored_trigger_values'` puis `./ci.sh`
- **Verification Proof**:
```text
Greptile local sur commit 8ed1ddc : Confidence 3/5, 1 constat P1 sur les ancres scalaires.
RED : alias scalaires pull_request_target et push reproduits à 0 erreur.
GREEN ciblé : 9 passed, 12 deselected.
CI finale : 6 étapes PASS, 48/48 tests, workflows 6/6 conformes.
Aucun push effectué.
```

### Step 11: Corriger le P1 sur les mappings concurrency flow multilignes
- [x] **Action**: Accumuler les mappings flow multilignes de `concurrency:` avant d'exiger un champ `group` non vide.
- [x] **Verify**: `./venv/bin/pytest -q tests/test_verify_workflows.py -k 'multiline_flow_concurrency_without_group or scalar_trigger_anchor_aliases or external_multiline_flow_sequence_anchor_alias or external_multiline_and_sequence_anchor_aliases or accept_concurrency_group_after_cancel_in_progress or block_anchored_trigger_alias or multiline_anchored_trigger_mapping or empty_concurrency_for_push or anchored_trigger_mapping or inline_anchored_trigger_values'` puis `./ci.sh`
- **Verification Proof**:
```text
Greptile local sur commit e0dac50 : Confidence 4/5, 1 constat P1 sur concurrency flow multiline.
RED : mapping flow multiline sans group reproduit à 0 erreur.
GREEN ciblé : 10 passed, 12 deselected.
CI finale : 6 étapes PASS, 49/49 tests, workflows 6/6 conformes.
Ruff Format intermédiaire échoué sur 1 ligne puis corrigé ; seconde CI entièrement PASS.
Aucun push effectué.
```

### Step 12: Corriger les P1 sur alias flow, collections on multilignes et group quoté
- [x] **Action**: Résoudre les alias dans les séquences flow, accumuler les collections flow multilignes sous `on:`, et décoder les clés `group` quotées dans les mappings `concurrency` inline et bloc.
- [x] **Verify**: `./venv/bin/pytest -q tests/test_verify_workflows.py -k 'flow_sequence_alias_trigger or multiline_flow_triggers or accept_quoted_concurrency_group or multiline_flow_concurrency_without_group or scalar_trigger_anchor_aliases or external_multiline_flow_sequence_anchor_alias or external_multiline_and_sequence_anchor_aliases or accept_concurrency_group_after_cancel_in_progress or block_anchored_trigger_alias or multiline_anchored_trigger_mapping or empty_concurrency_for_push or anchored_trigger_mapping or inline_anchored_trigger_values'` puis `./ci.sh`
- **Verification Proof**:
```text
Greptile local sur commit 1236d0a : Confidence 0/5, 3 constats P1.
RED : alias flow, group quoté et cas on flow multiline reproduits.
GREEN ciblé : 13 passed, 12 deselected.
CI finale : 6 étapes PASS, 52/52 tests, workflows 6/6 conformes.
C901 intermédiaire de _parse_triggers corrigé par extraction helper ; CI finale Ruff PASS.
Aucun push effectué.
```

### Step 13: Corriger les P1 sur alias flow imbriqué et groupe concurrency descendant
- [x] **Action**: Résoudre les alias imbriqués dans les ancres flow avec les ancres déjà connues, et limiter la validation du `group` aux propriétés directes de `concurrency`.
- [x] **Verify**: `./venv/bin/pytest -q tests/test_verify_workflows.py -k 'nested_alias_inside_flow_anchor or nested_concurrency_group_without_direct_group or flow_sequence_alias_trigger or multiline_flow_triggers or accept_quoted_concurrency_group or multiline_flow_concurrency_without_group or scalar_trigger_anchor_aliases or external_multiline_flow_sequence_anchor_alias or external_multiline_and_sequence_anchor_aliases or accept_concurrency_group_after_cancel_in_progress or block_anchored_trigger_alias or multiline_anchored_trigger_mapping or empty_concurrency_for_push or anchored_trigger_mapping or inline_anchored_trigger_values'` puis `./ci.sh`
- **Verification Proof**:
```text
Greptile local sur commit cdac9fd : Confidence 2/5, 2 constats P1.
RED : alias flow imbriqué et group descendant reproduits.
GREEN ciblé : 15 passed, 12 deselected.
CI finale : 6 étapes PASS, 54/54 tests, workflows 6/6 conformes.
Aucun push effectué.
```

### Step 14: Commit local et nouvelle revue Greptile sans push
- [x] **Action**: Créer un huitième commit local avec le correctif et exécuter une seule revue Greptile contre `main`; ne pas pousser.
- [x] **Verify**: Greptile doit atteindre 5/5 sans finding P1/P2, puis lire le résultat complet avant toute action distante.
- **Verification Proof**:
```text
Commit local final : 27c4380.
Greptile : Confidence 5/5.
No blocking failure remains.
No review comments.
CI locale précédente : 54/54 tests, workflows 6/6, Ruff, Ruff Format et Mypy PASS.
Quality gate du commit : Secrets, CVE, Ruff, Mypy, Sonar/Bugbear/Simplify, Bandit et Semgrep PASS.
Aucun push effectué.
```

### Step 15: Corriger le P1 sur la clé top-level `&events on:`
- [x] **Action**: Normaliser les ancres placées avant une clé YAML dans `decode_yaml_key()` et ajouter une régression `&events on:` contenant `pull_request_target`.
- [x] **Verify**: `./venv/bin/pytest -q tests/test_verify_workflows.py -k 'anchored_top_level_on_key or nested_escaped_event_keys_and_dispatch_inputs_not_confused or reject_pull_request_target'`
- **Verification Proof**:
```text
Greptile distant PR #36 : Confidence 3/5, P1 `&events on:`.
RED : 1 failed, 27 deselected ; le workflow privilégié était accepté avec 0 erreur.
GREEN : 3 passed, 25 deselected.
Les deux skills `.claude/skills/testsprite-onboard/SKILL.md` et `.claude/skills/testsprite-verify/SKILL.md` sont déjà supprimés du workspace et seront inclus dans le commit local.
Aucun push effectué.
```

### Step 16: Commit local et nouvelle revue Greptile sans push
- [x] **Action**: Exécuter `./ci.sh`, créer le commit local incluant le correctif, la régression, le GCC et les deux suppressions de skills, puis relire avec Greptile sans pousser.
- [x] **Verify**: CI complète PASS, commit sans fichier parasite, Greptile 5/5 sans blocage/commentaire.
- **Verification Proof**:
```text
Commit local : b9f0249.
CI : 6 étapes PASS, 55/55 tests, 6 workflows conformes.
Quality gate : Secrets, CVE, Ruff, Ruff Format, Mypy, Sonar/Bugbear/Simplify, Bandit et Semgrep PASS.
Suppressions incluses : .claude/skills/testsprite-onboard/SKILL.md et .claude/skills/testsprite-verify/SKILL.md.
Greptile : Confidence 5/5, No blocking failure remains, No review comments.
.gitignore reste volontairement non committé.
Aucun push effectué.
```

## 📐 Solution durable recommandée
Le correctif actuel est validé, mais le parseur texte reste une frontière fragile. Pour une évolution ultérieure hors de la PR #36, remplacer l'empilement de regex par un parseur YAML 1.2 réel, puis normaliser l'AST vers un modèle explicite (`triggers`, `permissions`, `concurrency.group`, `jobs`). Ajouter une matrice de fixtures couvrant ancres, alias, séquences/maps flow, clés quotées, expressions GitHub et commentaires ; conserver `./ci.sh` comme garde-fou. Ne pas mélanger cette refactorisation avec le push de la PR #36 validée.

- **Risque évité**: chaque nouvelle syntaxe YAML ne doit plus produire un nouveau correctif regex et un nouveau cycle Greptile.
- **Décision actuelle**: conserver `27c4380` pour la PR #36, planifier le parseur réel séparément après revue/autorisation.
