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
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RÉSUMÉ D'EXÉCUTION CI (CI Summary)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Étape de Validation                       | Statut     | Durée     |
|--------------------------------------------|------------|------------|
| Compilation Bytecode Python (compileall)   | PASS     | 161ms      |
| Validation Workflows GitHub Actions        | PASS     | 64ms       |
| Linter de Code (Ruff Check)                | PASS     | 74ms       |
| Formatage de Code (Ruff Format)            | PASS     | 56ms       |
| Typage Statique Strict (Mypy)              | PASS     | 14245ms    |
| Suite de Tests Pytest                      | PASS     | 67025ms    |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Toutes les étapes CI sont validées avec succès !
```

## ⚠️ Mitigations & Edge Cases
- **Risk & Mitigation**: Process group SIGKILL et vidange défensive contre les processus orphelins.
