# Execution Plan: Unification de la Spécification des Outils dans les READMEs

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: Parité bilingue stricte ligne à ligne (`wc -l README.md` == `wc -l README.fr.md`), 0 émoji Unicode dans les en-têtes Markdown (`#` à `####`), 0 mention d'historique de versions, et 100% de passage des tests CI (`./ci.sh`). Les sections « Core Capabilities » et « Fonctionnalités Principales » doivent présenter les 15 outils unifiés (13 primitives chirurgicales de `mcp_final_specification.md` + 2 outils vidéo continus de `maj.md`).
- **Pre-requisites**: `mcp_final_specification.md`, `note-de-conception-fondements-et-architecture.md`, `maj.md`, commit `fe5f9a3` sur `main`.

## 🛠️ Step-by-Step Sequence

### Step 1: Mise à jour de README.md et README.fr.md
- [x] **Action**: Remplacer la section des 21 outils monolithiques par les 15 outils unifiés structurés par couche (REPL `execute_action_batch`, PTY/Système, L3 AT-SPI, L2 OCR, L1 Matériel, Audit Vidéo) et mettre à jour les mentions textuelles associées.
- [x] **Verify**: `wc -l README.md && wc -l README.fr.md` et inspection du nombre de lignes.
- **Verification Proof**:
```text
447 README.md
447 README.fr.md
Parité stricte : 447 lignes dans les deux fichiers, correspondance parfaite des lignes vides.
```

### Step 2: Vérification de l'intégrité Markdown et absence d'émojis Unicode
- [x] **Action**: Exécuter un script de contrôle pour vérifier l'absence d'émojis Unicode dans les en-têtes, la symétrie des tableaux et l'absence de termes d'historique de version.
- [x] **Verify**: Script python de validation Markdown.
- **Verification Proof**:
```text
✓ Line count: 447 lines (both)
✓ Empty line structure matches 100%
✓ Zero Unicode emojis in markdown headings
✓ Table columns match 100% across all tables
✓ Zero version history keywords
All validation checks passed successfully!
```

### Step 3: Validation CI Locale Complète
- [x] **Action**: Exécuter `./ci.sh` (compileall, verify_workflows, ruff, mypy, pytest 112 tests).
- [x] **Verify**: `./ci.sh`
- **Verification Proof**:
```text
============================= 112 passed in 38.62s =============================
✔ Validé (40617ms)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RÉSUMÉ D'EXÉCUTION CI (CI Summary)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Étape de Validation                       | Statut     | Durée     |
|--------------------------------------------|------------|------------|
| Compilation Bytecode Python (compileall)   | PASS     | 343ms      |
| Validation Workflows GitHub Actions        | PASS     | 94ms       |
| Linter de Code (Ruff Check)                | PASS     | 18ms       |
| Formatage de Code (Ruff Format)            | PASS     | 22ms       |
| Typage Statique Strict (Mypy)              | PASS     | 570ms      |
| Suite de Tests Pytest                      | PASS     | 40617ms    |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Toutes les étapes CI sont validées avec succès !
```

### Step 4: Création de la PR et Résolution des Retours Greptile
- [x] **Action**: Commiter, pousser sur `docs/unify-tools-specification`, créer la PR #139 sous le compte `personnal-agent`, et réceptionner le rapport Greptile initial (Score 3/5, 3 constats identifiés).
- [x] **Action Corrective**: Traiter exhaustivement les 3 constats Greptile localement :
  1. *Finding 1 (P1)* : Qualification de la table des 15 outils comme Architecture Cible v1.0 avec badges `Target v1.0` / `Cible v1.0`, mention des alias runtime actifs `gui_*`, et ajout de la documentation exhaustive des 11 utilitaires runtime actifs (`gui_clipboard_*`, `gui_window_*`, `gui_find_template`, `gui_web_action`).
  2. *Finding 2 (P2)* : Matrice Section 5 de `mcp_final_specification.md` complétée avec les 12 cas limites réels (T-01 à T-03, S-01 à S-03, V-01 à V-03, O-01 à O-03).
  3. *Finding 3 (P1)* : Remplacement de `python-evdev` par `evdev` et ajout de l'installation de `gui-agent` dans Section 6.
- [x] **Verify**: `./ci.sh` (112/112 tests PASS) et `ALLOW_CONFIG_EDIT=1 ./.githooks/pre-commit` (8/8 couches validées).
- **Verification Proof**:
```text
======================== 112 passed in 74.10s (0:01:14) ========================
✔ Validé (76781ms)
[Quality-Gate] Pipeline validé avec succès (Secrets, CVE, Lint, Typage, Qualité, SAST). Commit autorisé.
```
- [ ] **Action**: Pousser le commit de correction sur `docs/unify-tools-specification`, observer la temporisation de 8 minutes (480s) et qualifier l'obtention du score Greptile 5/5.

## ⚠️ Mitigations & Edge Cases
- **Risk**: Greptile pourrait relever une incohérence entre les 15 outils documentés et l'exposition actuelle de 21 outils dans `linux/server.py`.
- **Mitigation**: Clarifier explicitement dans le texte d'introduction que le tableau décrit la spécification unifiée de l'architecture cible v1.0 avec badges explicites (`Target v1.0` / `Cible v1.0` vs `Active` / `Actif`), documenter les alias d'exécution runtime actifs (`gui_*`), et fournir la documentation complète des 11 utilitaires opérationnels actuels pour qu'aucun outil exposé ne disparaisse.
