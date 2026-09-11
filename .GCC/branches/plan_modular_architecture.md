# Execution Plan: Modular Architecture Scaffolding (Issue #129)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: `./ci.sh` 100% vert (Ruff, Mypy strict 17 fichiers, 65 tests). Arborescence modulaire importable.
- **Pre-requisites**: Branche `refactor/modular-architecture-issue-129`.

## 🛠️ Step-by-Step Sequence

### Step 1: Déploiement arborescence et modules initiaux
- [x] **Action**: `mkdir -p gui_agent/{core,layers,utils}` et création des modules initiaux typés.
- [x] **Verify**: `python3 -c "import gui_agent.core, gui_agent.layers, gui_agent.utils"`
- **Verification Proof**:
```text
Imports successfully loaded!
```

### Step 2: Ajustement dépendances et validation CI
- [x] **Action**: Mise à jour `pyproject.toml`, `install.sh`, `uv.lock`.
- [x] **Verify**: `./ci.sh`
- **Verification Proof**:
```text
65 passed in 19s (PASS 100%)
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Timeout REPL et PTY laissant des processus résiduels.
- **Mitigation**: Isolation subprocess et terminaison du groupe de processus avec `proc.wait()`.
