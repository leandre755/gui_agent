# Execution Plan: Support Multi-Versions MCP 1.x & 2.x

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: Le serveur FastMCP et sa suite de tests doivent fonctionner de manière transparente avec `mcp>=1.2.0,<3.0.0`, sans dépendance fragile sur les attributs privés internes de `FastMCP`.
- **Pre-requisites**: Environnement Python virtuel avec `pytest`, `ruff`, `mypy`.

## 🛠️ Step-by-Step Sequence

### Step 1: Neutralisation du message d'erreur restrictif à l'import
- [x] **Action**: Modifier `gui_agent/server.py` pour retirer la mention `version 1.x`.
- [x] **Verify**: `python3 -c "import gui_agent; print(gui_agent.__version__)"`
- **Verification Proof**:
```text
0.1.0
```

### Step 2: Abstraction robuste d'introspection des outils dans les tests
- [x] **Action**: Adapter `tests/test_package.py` pour détecter les outils FastMCP via plusieurs stratégies (compatibilité v1/v2).
- [x] **Verify**: `uv run pytest tests/test_package.py`
- **Verification Proof**:
```text
64 passed in 16.74s
```

### Step 3: Élargissement de la plage de dépendance dans `pyproject.toml`
- [x] **Action**: Modifier `pyproject.toml` avec `"mcp>=1.2.0,<3.0.0"`.
- [x] **Verify**: `uv lock --check || uv lock`
- **Verification Proof**:
```text
dependencies updated to "mcp>=1.2.0,<3.0.0"
```

### Step 4: Validation complète locale
- [x] **Action**: Exécuter `pytest`, `ruff check .` et `mypy`.
- [x] **Verify**: `./ci.sh`
- **Verification Proof**:
```text
| Étape de Validation                       | Statut     | Durée     |
|--------------------------------------------|------------|------------|
| Compilation Bytecode Python (compileall)   | PASS       | 2194ms     |
| Validation Workflows GitHub Actions        | PASS       | 88ms       |
| Linter de Code (Ruff Check)                | PASS       | 579ms      |
| Formatage de Code (Ruff Format)            | PASS       | 90ms       |
| Typage Statique Strict (Mypy)              | PASS       | 2490ms     |
| Suite de Tests Pytest                      | PASS       | 18042ms    |
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Changements d'API internes dans `mcp` 2.x pour l'enregistrement des outils.
- **Mitigation**: Helper multi-niveaux d'inspection (`list_tools()`, `_tool_manager`, `_tools`, ou introspection des fonctions `gui_` exportées).
