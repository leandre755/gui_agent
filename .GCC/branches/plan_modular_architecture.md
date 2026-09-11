# Execution Plan: Modular Architecture Scaffolding (Issue #129)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: CI 100% vert (Ruff, Mypy, Pytest). Arborescence modulaire importable.
- **Pre-requisites**: Branche `refactor/modular-architecture-issue-129`.

## 🛠️ Step-by-Step Sequence
### Step 1: Déploiement arborescence et modules initiaux
- [x] **Action**: `mkdir -p gui_agent/{core,layers,utils}` et création des modules initiaux typés.
- [x] **Verify**: `python3 -c "import gui_agent.core, gui_agent.layers, gui_agent.utils"`
- **Verification Proof**:
```text
$ python3 -c "import gui_agent.core, gui_agent.layers, gui_agent.utils"
```
### Step 2: Ajustement dépendances et validation CI
- [x] **Action**: Mise à jour `pyproject.toml`, `install.sh`, `uv.lock`.
- [x] **Verify**: `./ci.sh`
- **Verification Proof**:
```text
| Étape de Validation                       | Statut     | Durée     |
|--------------------------------------------|------------|------------|
| Compilation Bytecode Python (compileall)   | PASS     | 303ms      |
| Validation Workflows GitHub Actions        | PASS     | 84ms       |
| Linter de Code (Ruff Check)                | PASS     | 60ms       |
| Formatage de Code (Ruff Format)            | PASS     | 49ms       |
| Typage Statique Strict (Mypy)              | PASS     | 441ms      |
| Suite de Tests Pytest                      | PASS     | 63388ms    |
65 passed in 62.57s
```

## ⚠️ Mitigations & Edge Cases
- **Risk & Mitigation**: Process group SIGKILL et vidange défensive contre les processus orphelins.
