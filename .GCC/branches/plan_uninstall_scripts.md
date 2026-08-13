# Execution Plan: Uninstallation Scripts for Linux/macOS (`uninstall.sh`) and Windows (`uninstall.ps1`)

## 📋 Target Invariant & Pre-requisites
- **Target Invariant**: Fournir des scripts de désinstallation idempotents et sécurisés pour Linux/macOS (`uninstall.sh`) et Windows (`uninstall.ps1`) permettant la désinstallation isolée (`uv tool uninstall gui-agent`), le nettoyage des configurations clients MCP (Claude Code, Antigravity) et la purge optionnelle des données/screenshots.
- **Pre-requisites**: `uv`, `bash`, `pwsh`, tests unitaires opérationnels.

## 🛠️ Step-by-Step Sequence

### Step 1: Création du script de désinstallation Linux/macOS (`uninstall.sh`)
- [x] **Action**: Rédiger `uninstall.sh` avec options `--yes`, `--purge-data`, `--dry-run`, suppression de `uv tool`, désenregistrement Claude Code et nettoyage sécurisé de `~/.gemini/config/mcp_config.json`.
- [x] **Verify**: `chmod +x uninstall.sh && bash -n uninstall.sh && ./uninstall.sh --dry-run`
- **Verification Proof**:
```text
[INFO] 1/3 - Désinstallation du package 'gui-agent' via Astral 'uv'...
[INFO] [Dry-Run] /home/omni/.local/bin/uv tool uninstall gui-agent
[INFO] 2/3 - Nettoyage des configurations des clients MCP...
[INFO] [Dry-Run] claude mcp remove gui-agent
[INFO] [Dry-Run] Suppression de l'entrée 'gui-agent' dans ~/.gemini/config/mcp_config.json
[INFO] 3/3 - Nettoyage des données temporaires et captures d'écran...
[INFO] [Dry-Run] Purge possible du répertoire de captures : /home/omni/.local/share/gui-agent/screenshots
============================================================
     Désinstallation de GUI Agent terminée avec succès !    
============================================================
```

### Step 2: Création du script de désinstallation Windows (`uninstall.ps1`)
- [x] **Action**: Rédiger `uninstall.ps1` (et miroir dans `skills/gui-agent-windows-install/scripts/uninstall.ps1`) avec paramètres `-Yes`, `-PurgeData`, `-DryRun`, suppression de `uv tool`, nettoyage Claude Code et Antigravity JSON.
- [x] **Verify**: `pwsh -NoProfile -Command "[System.Management.Automation.Language.Parser]::ParseFile('$PWD/uninstall.ps1', [ref]\$null, [ref]\$null)"`
- **Verification Proof**:
```text
uninstall.ps1 AST: VALID
skills uninstall.ps1 AST: VALID
```

### Step 3: Mise à jour du Skill Windows (`SKILL.md`) et de la documentation `README.md`
- [x] **Action**: Ajouter la section de désinstallation dans `skills/gui-agent-windows-install/SKILL.md` et dans `README.md`.
- [x] **Verify**: `uv run --with ruff ruff check .`
- **Verification Proof**:
```text
All checks passed!
```

### Step 4: Mise à jour des tests et validation globale Zero-Slop
- [x] **Action**: Ajouter les assertions dans `tests/test_package.py`, exécuter `pytest` et le hook pre-commit 8 couches.
- [x] **Verify**: `ALLOW_CONFIG_EDIT=1 ./.githooks/pre-commit && ./venv/bin/pytest -v`
- **Verification Proof**:
```text
tests/test_package.py::test_installation_and_uninstallation_scripts_presence PASSED
============================== 7 passed in 3.15s ===============================
[Pre-Commit] Les 8 couches de validation Zero-Slop (Anti-leak, CVE, Ruff Lint, Format, Mypy, Sonar/Smells, Bandit, Semgrep) sont 100% validées.
```

## ⚠️ Mitigations & Edge Cases
- **Risk**: Suppression accidentelle de fichiers dans `~/.gemini/config/mcp_config.json` si d'autres serveurs MCP sont configurés.
- **Mitigation**: Manipulation ciblée du JSON via script Python en mémoire ne supprimant que la clé `mcpServers["gui-agent"]` tout en préservant le reste du dictionnaire.
- **Risk**: Erreur si le package n'est pas encore installé lors de l'exécution du désinstalleur.
- **Mitigation**: Exécution avec tolérance d'absence (`|| true` en shell, `try/catch` en PowerShell) pour garantir l'idempotence.
