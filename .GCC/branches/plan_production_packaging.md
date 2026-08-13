# Execution Plan: Production Packaging & Automated Installation (PyPI + uv tool + install.sh)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: Le serveur FastMCP GUI Agent doit être distribué sous forme de package standard Python (`gui-agent`) installable en environnement isolé via `uv tool install`, fournissant les points d'entrée CLI `gui-agent` et `mcp-gui-server`, accompagné d'un script d'installation automatisé `install.sh` idempotent et sécurisé.
- **Pre-requisites**: `uv` disponible sur le système, Python 3.13 / 3.10+, pre-commit hook 8 couches opérationnel.

## 🛠️ Step-by-Step Sequence

### Step 1: Restructuration du code en package Python standard (`gui_agent/`)
- [x] **Action**: Créer le package `gui_agent/` (`gui_agent/__init__.py`, `gui_agent/server.py`, `gui_agent/__main__.py`), adapter `SCREENSHOTS_DIR` pour la production (`~/.local/share/gui-agent/screenshots` avec override par variable d'environnement), et conserver `mcp_gui_server.py` à la racine comme wrapper de rétrocompatibilité.
- [x] **Verify**: `uv run --with ruff ruff check . && ./venv/bin/mypy gui_agent mcp_gui_server.py --ignore-missing-imports`
- **Verification Proof**:
```text
All checks passed!
Success: no issues found in 4 source files
```

### Step 2: Configuration `pyproject.toml`, métadonnées de release et `README.md`
- [x] **Action**: Configurer `[build-system]` (Hatchling), métadonnées `[project]`, dépendances core et optionnelles, scripts CLI (`gui-agent` et `mcp-gui-server`), et rédiger une documentation de production `README.md`.
- [x] **Verify**: `uv run --with ruff ruff check pyproject.toml && ./venv/bin/mypy gui_agent --ignore-missing-imports`
- **Verification Proof**:
```text
All checks passed!
Success: no issues found in 3 source files
```

### Step 3: Construction du package et validation de l'installation isolée (`uv tool install`)
- [x] **Action**: Construire les artefacts de distribution (sdist `.tar.gz` et wheel `.whl`) via `uv build` et tester l'installation isolée locale via `uv tool install . --force`.
- [x] **Verify**: `uv build && uv tool install . --force && ~/.local/bin/gui-agent`
- **Verification Proof**:
```text
Successfully built dist/gui_agent-0.1.0.tar.gz
Successfully built dist/gui_agent-0.1.0-py3-none-any.whl
Installed 2 executables: gui-agent, mcp-gui-server
gui_agent version: 0.1.0
Exported tools count: 24
FastMCP tools: 21
```

### Step 4: Création et validation du script d'installation automatisé `install.sh`
- [x] **Action**: Écrire un script `install.sh` robuste, idempotent et sécurisé (détection dépendances système apt/dnf/pacman, installation automatique de `uv` si absent, installation isolée de `gui-agent` via `uv tool install`, configuration guidée des clients MCP Claude Code & Antigravity).
- [x] **Verify**: `bash -n install.sh && ./install.sh --dry-run && ./install.sh -y --local`
- **Verification Proof**:
```text
[SUCCESS] Système d'exploitation compatible : Linux (x86_64)
[SUCCESS] Astral uv opérationnel : uv 0.12.3
[SUCCESS] Exécutables 'gui-agent' et 'mcp-gui-server' installés avec succès dans ~/.local/bin !
[SUCCESS] Serveur MCP configuré pour Claude Code.
[SUCCESS] Configuration Antigravity CLI mise à jour dans /home/omni/.gemini/config/mcp_config.json
```

### Step 5: Validation globale de l'intégrité et passage du hook Zero-Slop 8 couches
- [x] **Action**: Exécuter les tests E2E et le hook pre-commit Zero-Slop complet.
- [x] **Verify**: `ALLOW_CONFIG_EDIT=1 ./.githooks/pre-commit && ./venv/bin/pytest -v`
- **Verification Proof**:
```text
[Pre-Commit] Les 8 couches de validation Zero-Slop (Anti-leak, CVE, Ruff Lint, Format, Mypy, Sonar/Smells, Bandit, Semgrep) sont 100% validées.
============================== 5 passed in 1.86s ===============================
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Conflit de rétrocompatibilité pour les clients ou scripts important directement `mcp_gui_server.py`.
- **Mitigation**: `mcp_gui_server.py` reste à la racine et réexporte l'ensemble des symboles et points d'entrée de `gui_agent.server`.
- **Risk**: Chemins absolus résiduels (`/home/omni/...`) non portables sur d'autres machines cibles.
- **Mitigation**: Utilisation systématique de `os.path.expanduser("~/.local/share/gui-agent/screenshots")` ou `os.environ.get("GUI_AGENT_SCREENSHOTS_DIR")`.
