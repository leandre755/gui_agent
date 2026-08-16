# Execution Plan: Repository Organization & Quality Standardization

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**:
  1. `git_credential.json` reste strictement préservé en local, non tracké, et protégé contre tout staging Git.
  2. `CLAUDE.md` et `AGENTS.md` restent tous les deux présents à la racine pour garantir le support multi-agents (Claude Code & Antigravity).
  3. L'arborescence de tests est structurée (`tests/unit/`, `tests/integration/`, `tests/e2e/`), sans aucun chemin absolu `/home/omni/` en dur, et 100% validée sous pytest et `./ci.sh`.
  4. Les chemins protégés de gouvernance (`governance.yml`, `settings.json`, PR template) ciblent les fichiers réels (`.githooks/*`, `install.*`, `uninstall.*`, `ci.sh`).
  5. `release.yml` est adapté pour le build et la publication Python (`uv build`).
- **Pre-requisites**: `uv`, `./venv`, `xvfb-run` disponibles sur le système hôte.

## 🛠️ Step-by-Step Sequence

### Step 1: Restructuration de la Suite de Tests (`tests/`) et Nettoyage de `examples/`
- [ ] **Action**:
  - Déplacer `tests/test_package.py` vers `tests/unit/test_package.py` et adapter les assertions.
  - Créer `tests/integration/test_evolutions.py` à partir de `examples/test_evolutions.py` (remplacer `sys.path.append("/home/omni/...")` par `import gui_agent` et assainir les chemins temporaires).
  - Créer `tests/integration/test_gui_agent.py` à partir de `examples/test_gui_agent.py` (import direct `gui_agent`).
  - Créer `tests/e2e/test_e2e_validation.py` à partir de `examples/test_e2e_validation.py` (import `gui_agent`, validation 4 briques).
  - Créer `examples/desktop_automation_demo.py` (exemple utilisateur portable et documenté).
  - Supprimer les anciens fichiers de tests redondants dans `examples/` (`capture_to_artifacts.py`, `test_e2e_validation.py`, `test_evolutions.py`, `test_gui_agent.py`).
- [ ] **Verify**: `xvfb-run -a ./venv/bin/pytest -v tests/`
- **Verification Proof**:
```text
(En attente d'exécution)
```

### Step 2: Harmonisation de la Gouvernance, Templates et Permissions Agent
- [ ] **Action**:
  - Mettre à jour `.github/workflows/governance.yml` (L61) : remplacer `githooks/*|setup.sh|setup.ps1` par `.githooks/*|install.sh|install.ps1|uninstall.sh|uninstall.ps1|ci.sh`.
  - Mettre à jour `.agents/settings.json` et `.coding-stuff/antigravity-permissions.example.json` : aligner les règles `deny` sur `.githooks/`, `install.*`, `uninstall.*`, `ci.sh`.
  - Mettre à jour `.github/ISSUE_TEMPLATE/config.yml` : remplacer `OWNER/REPOSITORY` par `leandre755/gui_agent`.
  - Mettre à jour `.github/PULL_REQUEST_TEMPLATE.md` : aligner la checklist sur les noms réels des scripts.
  - Mettre à jour `.github/CODEOWNERS` : inclure `ci.sh`.
- [ ] **Verify**: `./venv/bin/python .github/scripts/verify_workflows.py`
- **Verification Proof**:
```text
(En attente d'exécution)
```

### Step 3: Refonte de `release.yml` et Consolidation de `.gitignore`
- [ ] **Action**:
  - Réécrire `.github/workflows/release.yml` pour l'écosystème Python (`uv build` + publication GitHub Release des artefacts wheel/sdist).
  - Compléter `.gitignore` : ajouter les dossiers de cache `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `dist/`, `build/`, `*.egg-info/`, `.coverage`, et débloquer le suivi des schémas vectoriels dans `assets/`.
- [ ] **Verify**: `./ci.sh && ALLOW_CONFIG_EDIT=1 ./.githooks/pre-commit`
- **Verification Proof**:
```text
(En attente d'exécution)
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Casse éventuelle de rétrocompatibilité pour les anciens scripts importants `mcp_gui_server`.
- **Mitigation**: Le shim `mcp_gui_server.py` est conservé à la racine pour préserver la compatibilité historique locale.
- **Risk**: Risque de fuite de tokens lors des commits.
- **Mitigation**: `git_credential.json` reste strictement exclu dans `.gitignore` et surveillé par la couche 1 anti-leak du pre-commit.
