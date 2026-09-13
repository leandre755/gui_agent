# Execution Plan: Mise à Jour des README & Nouveaux Diagrammes Excalidraw (Architecture v1.0)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: Préservation stricte de l'isomorphisme bilingue ligne à ligne (`wc -l README.md` == `wc -l README.fr.md`), 0 emoji Unicode dans les en-têtes (utilisation exclusive des émojis animés Microsoft Fluent 3D), palette Émeraude (`#10B981` / `#34D399` / `#0D1117`), couverture exhaustive des nouveautés architecturales (`maj.md`, `note-de-conception-fondements-et-architecture.md`, Phase 1 AT-SPI Rust, chemins dynamiques XDG, nouveaux outils et scripts d'installation/désinstallation dédiés par OS), et validation complète de `./ci.sh` (112/112 tests PASS, Ruff, Mypy).
- **Pre-requisites**: Branche `docs/readme-how-it-works-update`, outils `gh`, `browser` subagent, suites de tests locales.

## 🛠️ Step-by-Step Sequence

### Step 1: Création de la Branche et Enregistrement du Plan dans GCC
- [x] **Action**: Création de la branche `docs/readme-how-it-works-update`, rédaction de `.GCC/branches/plan_readme_maj.md` et référencement dans `.GCC/main.md`.
- [x] **Verify**: `git status && test -f .GCC/branches/plan_readme_maj.md`
- **Verification Proof**:
```text
Sur la branche docs/readme-how-it-works-update
Fichier plan_readme_maj.md créé.
```

### Step 2: Conception & Génération des Nouveaux Diagrammes Excalidraw (EN & FR)
- [x] **Action**: Génération des diagrammes vectoriels SVG d'architecture reflétant les 2 Piliers (Escalade Progressive L3 AT-SPI Rust -> L2 RapidOCR -> L1 uinput/MSS, Moteur REPL Local CodeAct `execute_script`), la couche PTY, l'enregistrement vidéo continu et l'arborescence multi-plateforme (`linux/`, `windows/`, `macos/`).
- [x] **Verify**: Validation de l'arborescence SVG, hébergement/accès et inspection visuelle.
- **Verification Proof**:
```text
how-it-works-en.excalidraw & how-it-works-fr.excalidraw générés.
Rendu sur excalidraw.com et extraction SVG/PNG :
  - assets/exc-how-it-works-en.svg (44 200 octets)
  - assets/exc-how-it-works-fr.svg (45 225 octets)
Publication sur GitHub Gist Public :
  - EN: https://gist.githubusercontent.com/personnal-agent/f0b933b981a70de123282eb99fd6df44/raw/exc-how-it-works-en.svg
  - FR: https://gist.githubusercontent.com/personnal-agent/f0b933b981a70de123282eb99fd6df44/raw/exc-how-it-works-fr.svg
Inspection visuelle multimodale validée (palette Émeraude, Virgil font, rough sketches).
```

### Step 3: Rédaction et Mise à Jour de `README.md` (Version Anglaise)
- [x] **Action**: Intégration dans `README.md` des nouvelles sections d'architecture : Arborescence racine étanche (`linux/`, `windows/`, `macos/`), résolution dynamique des chemins XDG (`paths.py`), médiation d'accessibilité AT-SPI2 / D-Bus en Rust (`gui-agent-atspi`), les 2 Piliers conceptuels (Escalade Progressive L3/L2/L1 & Moteur REPL CodeAct), nouveaux scripts d'installation/désinstallation (`linux/install.sh`, `linux/uninstall.sh`, `windows/install.ps1`, `windows/uninstall.ps1`), mise à jour de la table des outils (accessibilité, vidéo préservée) et nouveau diagramme Excalidraw.
- [x] **Verify**: `wc -l README.md` et vérification syntaxique
- **Verification Proof**:
```text
README.md mis à jour : 485 lignes, 0 emoji Unicode dans les en-têtes (#/##/###/####), aucune mention de "Nouvelle version/maj", image SVG Gist configurée.
```

### Step 4: Rédaction et Synchronisation Isomorphe de `README.fr.md` (Version Française)
- [x] **Action**: Traduction technique soignée dans `README.fr.md` avec préservation stricte de la structure ligne par ligne en miroir parfait avec `README.md`.
- [x] **Verify**: `diff <(wc -l README.md | awk '{print $1}') <(wc -l README.fr.md | awk '{print $1}')`
- **Verification Proof**:
```text
File 1 (README.md): 485 lines
File 2 (README.fr.md): 485 lines
PERFECT MATCH on line count!
PERFECT MATCH on empty line structure!
```

### Step 5: Validation CI et Zero-Slop
- [x] **Action**: Exécution complète de `./ci.sh` et vérification des workflows GitHub Actions.
- [x] **Verify**: `./ci.sh`
- **Verification Proof**:
```text
| Étape de Validation                       | Statut     | Durée     |
|--------------------------------------------|------------|------------|
| Compilation Bytecode Python (compileall)   | PASS       | 560ms      |
| Validation Workflows GitHub Actions        | PASS       | 83ms       |
| Linter de Code (Ruff Check)                | PASS       | 19ms       |
| Formatage de Code (Ruff Format)            | PASS       | 23ms       |
| Typage Statique Strict (Mypy)              | PASS       | 955ms      |
| Suite de Tests Pytest                      | PASS       | 44572ms    |
============================= 112 passed in 41.60s =============================
🎉 Toutes les étapes CI sont validées avec succès !
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Divergence du nombre de lignes entre l'anglais et le français due aux longueurs de phrases.
- **Mitigation**: Ajustement minutieux des retours à la ligne et des paragraphes pour assurer `wc -l README.md == wc -l README.fr.md`.
- **Risk**: Liens d'images brisés ou indisponibilité CDN.
- **Mitigation**: Utilisation d'hébergement SVG fiable (GitHub Gist public) avec fallback local si nécessaire.
