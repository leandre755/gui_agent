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

### Step 4: Création de la PR et Suivi Greptile
- [ ] **Action**: Commiter, pousser sur `docs/unify-tools-specification`, créer la PR sous le compte `personnal-agent`, observer la temporisation de 8 minutes (480s) et qualifier le score Greptile 5/5.
- [ ] **Verify**: `gh pr view --json statusCheckRollup,reviews` et lecture intégrale des retours.
- **Verification Proof**:
```text
(En attente d'exécution)
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Greptile pourrait relever une incohérence entre les 15 outils documentés et l'exposition actuelle de 21 outils dans `linux/server.py`.
- **Mitigation**: Clarifier explicitement dans le texte d'introduction que le tableau décrit la spécification unifiée de l'architecture v1.0 avec son statut par couche (les primitives L3, L2, L1 screenshots et Vidéo étant actives, et l'implémentation complète des signatures cibles étant ordonnancée dans la feuille de route modulaire avec rétrocompatibilité des alias existants).
