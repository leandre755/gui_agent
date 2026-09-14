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
- [x] **Action Corrective**: Traiter exhaustivement les constats Greptile successifs :
  1. *Findings initiaux PR #139 (commit e5acb1f)* : Qualification de la table en Architecture Cible v1.0, matrice 12/12 cas réels dans `mcp_final_specification.md`, et correction de l'installation `evdev`.
  2. *Constats structurels Greptile (commit 5193e7d)* :
     - Remplacement de `execute_script` par le nom canonique `execute_action_batch` dans la prose du Pilier II (L81).
     - Rétablissement du bloc `<details>` et `<summary>` pour `Target Architecture v1.0 Primitives (13 tools)` sous `## Toolset & CLI Reference`.
     - Fermeture stricte de toutes les balises `<details>`, positionnement de `## Toolset & CLI Reference` au premier plan (hors de tout volet pliable), et préservation des 5 blocs d'outils opérationnels.
     - Budget diff de gouvernance maintenu à 598 lignes (< 1000 lignes) et parité bilingue stricte à 582 lignes.
- [x] **Verify**: `./ci.sh` (112/112 tests PASS) et `ALLOW_CONFIG_EDIT=1 ./.githooks/pre-commit` (8/8 couches validées).
- **Verification Proof**:
```text
============================= 112 passed in 58.41s =============================
✔ Validé (71198ms)
[Quality-Gate] Pipeline validé avec succès (Secrets, CVE, Lint, Typage, Qualité, SAST). Commit autorisé.
```
- [ ] **Action**: Pousser le commit de correction sur `docs/unify-tools-specification`, observer la temporisation de 8 minutes (480s) et qualifier l'obtention du score Greptile 5/5.

## ⚠️ Mitigations & Edge Cases
- **Risk**: Greptile pourrait relever une incohérence entre les 15 outils documentés et l'exposition actuelle de 21 outils dans `linux/server.py`.
- **Mitigation**: Clarifier explicitement dans le texte d'introduction que le tableau décrit la spécification unifiée de l'architecture cible v1.0 avec badges explicites (`Target v1.0` / `Cible v1.0` vs `Active` / `Actif`), documenter les alias d'exécution runtime actifs (`gui_*`), et fournir la documentation complète des 11 utilitaires opérationnels actuels pour qu'aucun outil exposé ne disparaisse.
