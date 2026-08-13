# Execution Plan: Skill & Automation for Windows Installation (`gui-agent-windows-install`)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: Fournir un skill complet `skills/gui-agent-windows-install/SKILL.md` (conforme aux spécifications agentskills.io) et un script PowerShell d'installation automatisée `install.ps1` permettant le déploiement isolé et la configuration MCP de `gui-agent` sur Windows 10/11 sans erreur.
- **Pre-requisites**: Astral `uv`, PowerShell 5.1/7+, pre-commit hook 8 couches opérationnel.

## 🛠️ Step-by-Step Sequence

### Step 1: Création du script PowerShell d'installation automatisé `install.ps1`
- [x] **Action**: Rédiger `install.ps1` (et miroir dans `skills/gui-agent-windows-install/scripts/install.ps1`) avec détection des dépendances Windows (Winget: FFmpeg, Tesseract), installation de `uv`, déploiement isolé `uv tool install` et injection des configurations MCP pour Claude Code et Antigravity.
- [x] **Verify**: Vérification de la complétude du script et conformité syntaxique PowerShell.
- **Verification Proof**:
```text
install.ps1 AST: VALID
skills install.ps1 AST: VALID
PowerShell 7.4.6 runtime guard: [ERROR] Ce script d'installation est réservé aux environnements Microsoft Windows 10/11.
```

### Step 2: Rédaction du Skill d'installation Windows (`skills/gui-agent-windows-install/SKILL.md`)
- [x] **Action**: Rédiger `skills/gui-agent-windows-install/SKILL.md` avec frontmatter Agent Skills, déclencheurs précis, rôle, règles, workflows d'installation manuelle et automatisée, gestion des variables d'environnement Windows (`%LOCALAPPDATA%`), 2 exemples Input/Output complets et checklist d'auto-validation.
- [x] **Verify**: Validation de la structure du Skill (frontmatter, role, 2+ few-shot examples, validation checklist).
- **Verification Proof**:
```text
tests/test_package.py::test_windows_skill_structure PASSED [100%]
```

### Step 3: Intégration dans `README.md` et mise à jour des tests
- [x] **Action**: Documenter la méthode d'installation Windows dans [`README.md`](file:///home/omni/Code/gui_agent/README.md) et ajouter un test de validation des artefacts dans [`tests/test_package.py`](file:///home/omni/Code/gui_agent/tests/test_package.py).
- [x] **Verify**: `./venv/bin/pytest -v`
- **Verification Proof**:
```text
============================== 7 passed in 6.69s ===============================
```

### Step 4: Validation de l'intégrité globale et passage du hook Zero-Slop 8 couches
- [x] **Action**: Exécuter le hook pre-commit Zero-Slop 8 couches.
- [x] **Verify**: `ALLOW_CONFIG_EDIT=1 ./.githooks/pre-commit`
- **Verification Proof**:
```text
[Pre-Commit] Les 8 couches de validation Zero-Slop (Anti-leak, CVE, Ruff Lint, Format, Mypy, Sonar/Smells, Bandit, Semgrep) sont 100% validées.
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Différence de gestion des chemins et variables d'environnement sous Windows (`%USERPROFILE%`, `AppData\Local`).
- **Mitigation**: Utilisation explicite de `[System.Environment]::GetFolderPath` et variables de session dans `install.ps1` et `SKILL.md`.
- **Risk**: Politique d'exécution des scripts PowerShell (`ExecutionPolicy Restricted`).
- **Mitigation**: Documenter l'utilisation de `-ExecutionPolicy Bypass` dans les instructions et one-liners.
