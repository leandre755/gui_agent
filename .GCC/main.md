# Current Project Context

## 🏆 Major Milestones (Archived Epics)
- [2026-08-14] Refonte complète de la vitrine README en mode Landing Page UX bilingue isomorphique ([`README.md`](file:///home/omni/Code/gui_agent/README.md) et [`README.fr.md`](file:///home/omni/Code/gui_agent/README.fr.md)) selon le standard `build-readme`, palette Émeraude (`#10B981` / `#34D399` / `#0D1117`), 0 emoji d'en-tête, 21 outils cartographiés et 100% Zero-Slop 8 couches validé.
- [2026-08-13] Création et publication de la Release GitHub `v0.1.0` ([Releases](https://github.com/leandre755/gui_agent/releases/tag/v0.1.0)) avec artefacts sdist/wheel et validation à 100% du pipeline CI/CD GitHub Actions (`CI` vert, `Release` vert, `Workflow hygiene` vert).
- [2026-08-13] Publication et push complets sur GitHub (`origin/main`) : Commits atomiques `feat(release)` (packaging production 0.1.0, scripts de cycle de vie multiplateformes, tests) et `feat(governance)` (CI/CD GitHub Actions, dependabot, agent policies, CODEOWNERS) avec validation 100% Zero-Slop 8 couches.
- [2026-08-13] Configuration complète du starter-kit de gouvernance et CI/CD `coding-stuff` (politique accompagnée `AGENT_POLICY.md`, adaptateur `.agents/rules/coding-stuff-policy.md`, 6 workflows GitHub Actions conformes et sécurisés, templates d'issues, dependabot durci).
- [2026-08-13] Création et validation des scripts de désinstallation propre multiplateformes [`uninstall.sh`](file:///home/omni/Code/gui_agent/uninstall.sh) (Linux/macOS) et [`uninstall.ps1`](file:///home/omni/Code/gui_agent/uninstall.ps1) (Windows PowerShell) avec nettoyage automatique des configurations MCP (Claude Code, Antigravity) et option de purge des données.
- [2026-08-13] Création et validation complète du Skill d'installation Windows `gui-agent-windows-install` et consolidation dans [`INSTALL.md`](file:///home/omni/Code/gui_agent/INSTALL.md) et [`install.ps1`](file:///home/omni/Code/gui_agent/install.ps1).
- [2026-08-13] Mise en production du package Python standard `gui-agent` (build `uv build` sdist/wheel, distribution `uv tool install`, points d'entrée CLI `gui-agent` et `mcp-gui-server`, script d'installation automatisé `install.sh` et documentation `README.md`).
- [2026-08-13] Mise en place, remédiation et validation à 100% du hook pre-commit 8 couches Zero-Slop (Anti-leak, CVE, Ruff, Format, Mypy, Sonar/Smells, Bandit, Semgrep) avec détection stricte des commentaires d'inhibition.
- [2026-08-13] Campagne de qualification complète et validée à 100% (21/21 PASS) des outils MCP GUI par 21 sous-agents séquentiels dédiés.
- [2026-08-13] Extraction OCR/Visuelle et transmission complète (texte + image du coupon CapCut) au contact "Ape Ive" via WhatsApp Web avec preuve visuelle.
- [2026-08-13] Enregistrement et qualification du serveur MCP `gui-agent` dans la configuration globale Antigravity CLI (`~/.gemini/config/mcp_config.json`).
- [2026-08-12] Résolution et validation E2E à 100% des 4 défauts techniques (DEF-01 à DEF-04) du serveur MCP GUI.
- [2026-08-12] Campagne de qualification et test des 21 outils MCP GUI du serveur `gui-agent` via le client Claude Code CLI.
- [2026-08-11] Configuration et intégration du serveur MCP `gui-agent` dans Claude Code CLI (`claude mcp add`).
- [2026-08-11] Implémentation complète et validation E2E du serveur MCP GUI Computer Use Monolithique (`mcp_gui_server.py`).

## 🎯 Objective
Fournir un serveur MCP GUI monolithique FastMCP complet et léger, optimisé pour les environnements Linux X11/XWayland et Windows sur des architectures à ressources limitées (Intel i5 dual-core, ~3 Go RAM disponible), directement connecté à Claude Code et Antigravity CLI comme client MCP.

## 🧠 Decisions Made
- [2026-08-13] Scripts de désinstallation propre et atomique (uninstall.sh / uninstall.ps1)
  - **Context**: Offrir un mécanisme de désinstallation et nettoyage complet pour Linux/macOS et Windows sans laisser de configurations résiduelles.
  - **Rationale**: Désinstallation isolée via `uv tool uninstall gui-agent`, retrait automatique des entrées MCP dans Claude Code et `mcp_config.json` d'Antigravity, et option de purge ciblée du dossier de captures (`--purge-data`).
- [2026-08-13] Skill d'installation Windows & Automatisation PowerShell (install.ps1)
  - **Context**: Permettre le déploiement et la configuration de `gui-agent` sur Windows 10/11 en une seule ligne de commande PowerShell.
  - **Rationale**: Script PowerShell `install.ps1` combinant Winget (FFmpeg, Tesseract), téléchargement d'Astral `uv`, `uv tool install` isolé et mise à jour JSON automatique pour Claude Code et Antigravity CLI, encapsulé dans un Skill `SKILL.md` documenté selon la spécification `agentskills.io`.
- [2026-08-13] Distribution de Production via Package PyPI + uv tool install + install.sh
  - **Rationale**: Packaging standardisé `pyproject.toml` (Hatchling/UV), génération des artifacts wheel/sdist via `uv build`, installation isolée instantanée via `uv tool install gui-agent` avec exposition des binaires `gui-agent` et `mcp-gui-server` dans `~/.local/bin`, et automatisation de bout en bout via `install.sh`.
- [2026-08-13] Test séquentiel par 21 sous-agents dédiés
  - **Rationale**: Lancement d'un seul sous-agent à la fois, enregistrement immédiat du rapport de test et destruction de l'instance avant le lancement du sous-agent suivant.
- [2026-08-13] Integration Antigravity CLI Global MCP (`mcp_config.json`)
  - **Rationale**: Inscription stdio dans `~/.gemini/config/mcp_config.json` ciblant l'exécutable `gui-agent`.
- [2026-08-13] Pre-Commit 8 couches Zero-Slop via UV & Ruff étendu (Python)
  - **Rationale**: Ruff (Rust) offre une vitesse d'exécution <15ms tout en couvrant les règles Sonar/Bugbear/Simplify, combiné à Mypy (typage strict), Bandit (AST sécurité) et Semgrep (SAST).

## 🌿 Active Branches / Plans
- `readme-overhaul` : Refonte complète de la vitrine README en mode Landing Page UX bilingue isomorphique ([plan_readme_overhaul.md](file:///home/omni/Code/gui_agent/.GCC/branches/plan_readme_overhaul.md))
- `uninstall-scripts` : Création des scripts de désinstallation multiplateformes `uninstall.sh` et `uninstall.ps1` ([plan_uninstall_scripts.md](file:///home/omni/Code/gui_agent/.GCC/branches/plan_uninstall_scripts.md))

## 📈 Current Status
- ✅ Done: 
  - Restructuration du package Python standard `gui_agent/` avec export des 21 outils FastMCP.
  - Configuration de `pyproject.toml` (Hatchling backend, métadonnées, `dependencies`, `[project.scripts]`).
  - Construction des artefacts sdist (`gui_agent-0.1.0.tar.gz`) et wheel (`gui_agent-0.1.0-py3-none-any.whl`).
  - Validation de l'installation isolée via `uv tool install . --force` et vérification des exécutables `gui-agent` et `mcp-gui-server`.
  - Création et validation des scripts d'installation `install.sh` (Linux) et `install.ps1` (Windows PowerShell).
  - Création et validation des scripts de désinstallation `uninstall.sh` (Linux/macOS) et `uninstall.ps1` (Windows PowerShell).
  - Consolidation de la documentation complète d'installation et de dépannage dans [`INSTALL.md`](file:///home/omni/Code/gui_agent/INSTALL.md).
  - Rédaction complète du `README.md` et `LICENSE`.
  - Validation 100% de la suite de tests (`pytest` 7/7) et du hook Zero-Slop 8 couches.
- 🔄 In progress: 
  - Aucun.
- ⏳ Pending (Roadmap des versions futures) :
  - **1. Support complet Windows Natif (21/21 outils)** :
    - Gestion des fenêtres native (`pygetwindow` ou Win32 API `user32.dll` pour `gui_window_list`, `focus`, `close`, `resize_move`).
    - Capture vidéo native via `ffmpeg -f gdigrab`.
  - **2. Linux Universel & Wayland (sans dépendance stricte X11)** :
    - Support des environnements Wayland purs via `ydotool` (uinput), `wl-clipboard` et portails XDG Desktop / PipeWire pour la capture d'écran et vidéo.
  - **3. Support macOS Natif** :
    - Gestion des fenêtres et raccourcis via les APIs macOS Quartz / Accessibility API / `pyobjc`.
    - Capture vidéo via `ffmpeg -f avfoundation`.
  - **4. Publication officielle PyPI (pypi.org)** :
    - Téléversement via `uv publish --token <PYPI_API_TOKEN>`.

## 👉 Next Session Direction
La version `v0.1.0` de production est validée, taggée et poussée sur GitHub. La prochaine phase architecturale portera sur l'abstraction multiplateforme du gestionnaire de fenêtres (Linux X11/Wayland, Windows Win32, macOS) pour unifier les 21 outils de manière universelle.

