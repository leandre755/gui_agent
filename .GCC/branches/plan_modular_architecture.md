# Execution Plan: Modular Architecture Scaffolding (Issue #129)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: CI 100% vert (Ruff, Mypy, Pytest). Arborescence modulaire importable.
- **Pre-requisites**: Branche `refactor/modular-architecture-issue-129`. Restauration complète du contexte (Protocole A) validée avant toute modification hors `.GCC/`.

## 🛠️ Step-by-Step Sequence

### Step 0: Validation des prérequis et verrouillage d'alignement (Protocole A)
- [x] **Action**: Vérification de l'alignement GCC et interdiction de modifications hors `.GCC/` avant confirmation.
- [x] **Verify**: `python3 -c "c1 = open('.GCC/main.md', encoding='utf-8').read(); c2 = open('.GCC/resume.md', encoding='utf-8').read(); assert len(c1) > 100 and len(c2) > 100; print('PASS')"`
- **Verification Proof**:
```text
PASS
```

### Step 1: Restauration du macro-état projet (Protocole A - Étape 1)
- [x] **Action**: Lecture de `.GCC/main.md` pour charger les objectifs, milestones et branches actives.
- [x] **Verify**: `python3 -c "content = open('.GCC/main.md', encoding='utf-8').read(); assert len(content) > 100 and '## 🎯 Objective' in content; print('PASS')"`
- **Verification Proof**:
```text
PASS
```

### Step 2: Restauration de l'état de transition technique (Protocole A - Étape 2)
- [x] **Action**: Lecture de `.GCC/resume.md` pour charger les directives de transition immédiates.
- [x] **Verify**: `python3 -c "content = open('.GCC/resume.md', encoding='utf-8').read(); assert len(content) > 100 and '## 🎯 Functional Outcome' in content; print('PASS')"`
- **Verification Proof**:
```text
PASS
```

### Step 3: Déploiement arborescence et modules initiaux
- [x] **Action**: `mkdir -p gui_agent/{core,layers,utils}` et création des modules initiaux typés.
- [x] **Verify**: `python3 -c "import gui_agent.core, gui_agent.layers, gui_agent.utils; print('PASS')"`
- **Verification Proof**:
```text
PASS
```

### Step 4: Ajustement dépendances et validation CI
- [x] **Action**: Ajout de la dépendance conditionnelle `evdev` dans `pyproject.toml`, synchronisation de `uv.lock`, et mise à jour des paquets système dans `install.sh`.
- [x] **Verify**: `uv lock --check && ./ci.sh`
- **Verification Proof**:
```text
$ uv lock --check
Resolved 100 packages in 1ms
```
```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RÉSUMÉ D'EXÉCUTION CI (CI Summary)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Étape de Validation                       | Statut     | Durée     |
|--------------------------------------------|------------|------------|
| Compilation Bytecode Python (compileall)   | PASS     | 209ms      |
| Validation Workflows GitHub Actions        | PASS     | 82ms       |
| Linter de Code (Ruff Check)                | PASS     | 123ms      |
| Formatage de Code (Ruff Format)            | PASS     | 62ms       |
| Typage Statique Strict (Mypy)              | PASS     | 572ms      |
| Suite de Tests Pytest                      | PASS     | 36352ms    |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 Toutes les étapes CI sont validées avec succès !
```

## ⚠️ Mitigations & Edge Cases
- **Risk & Mitigation**: Process group SIGKILL et vidange défensive contre les processus orphelins.
