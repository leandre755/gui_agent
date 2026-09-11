# Execution Plan: Modular Architecture Scaffolding & Dependencies Update (Issue #129)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: L'intégralité de la suite CI locale (`./ci.sh`) doit rester strictement verte (compilation, linter Ruff, formatage, Mypy strict et tests Pytest). L'importation de `gui_agent` doit fonctionner sans rupture.
- **Pre-requisites**: Branche `refactor/modular-architecture-issue-129` créée à partir de `main`.

## 🛠️ Step-by-Step Sequence

### Step 1: Création de la branche dédiée et des dossiers modulaires
- [x] **Action**: `git checkout -b refactor/modular-architecture-issue-129 && mkdir -p gui_agent/core gui_agent/layers gui_agent/utils`
- [x] **Verify**: `git status`
- **Verification Proof**:
```text
Sur la branche refactor/modular-architecture-issue-129
Fichiers non suivis:
	gui_agent/core/
	gui_agent/layers/
	gui_agent/utils/
```

### Step 2: Échafaudage des fichiers squelettes typés
- [x] **Action**: Créer les fichiers `__init__.py` et modules initiaux (`core/repl.py`, `core/mcp_core.py`, `core/pty_session.py`, `layers/accessibility.py`, `layers/visual_perception.py`, `layers/input_emulation.py`, `layers/window_management.py`, `utils/human_mimic.py`, `utils/coordinates.py`, `utils/video.py`).
- [x] **Verify**: `python3 -c "import gui_agent.core, gui_agent.layers, gui_agent.utils"`
- **Verification Proof**:
```text
Imports successfully loaded!
All checks passed!
16 files already formatted
Success: no issues found in 16 source files
```

### Step 3: Migration des dépendances dans pyproject.toml et scripts
- [x] **Action**: Retirer `playwright`, remplacer `pytesseract` par `rapidocr-onnxruntime`, ajouter `evdev`. Mettre à jour `install.sh`.
- [x] **Verify**: `uv run --with ruff ruff check` & résolution uv
- **Verification Proof**:
```text
Resolved 14 packages in 1.80s
Installed 11 packages (evdev==2.0.0, rapidocr-onnxruntime==1.4.4, onnxruntime==1.30.0)
All checks passed!
```

### Step 4: Validation de l'isolation et tests de non-régression
- [x] **Action**: Exécuter la suite complète des tests et vérifications statiques.
- [x] **Verify**: `./ci.sh`
- **Verification Proof**:
```text
| Étape de Validation                       | Statut     | Durée     |
|--------------------------------------------|------------|------------|
| Compilation Bytecode Python (compileall)   | PASS     | 6640ms     |
| Validation Workflows GitHub Actions        | PASS     | 159ms      |
| Linter de Code (Ruff Check)                | PASS     | 847ms      |
| Formatage de Code (Ruff Format)            | PASS     | 267ms      |
| Typage Statique Strict (Mypy)              | PASS     | 51417ms    |
| Suite de Tests Pytest                      | PASS     | 49516ms    |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Toutes les étapes CI sont validées avec succès ! (65 passed in 44.45s)
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: `evdev` ou `rapidocr-onnxruntime` peuvent nécessiter des headers C ou des modèles ONNX volumineux lors du build.
- **Mitigation**: Utiliser `evdev` avec les roues binaires standard et spécifier des versions compatibles Python 3.10-3.13 sans compilation externe bloquante.
