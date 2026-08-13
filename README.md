# GUI Agent (FastMCP Linux Computer Use Server)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Standard](https://img.shields.io/badge/MCP-1.2.0+-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**GUI Agent** (`gui-agent` / `mcp-gui-server`) est un serveur MCP (Model Context Protocol) monolithique basé sur [FastMCP](https://github.com/jlowin/fastmcp), conçu pour offrir un contrôle graphique (Computer Use) complet, fluide et ultra-léger sur les environnements de bureau Linux (X11 et XWayland).

Il permet aux modèles de langage (Claude Code, Antigravity, Cursor, etc.) d'interagir nativement avec l'interface graphique : capture d'écran avec grille de coordonnées cartésiennes, pilotage souris/clavier au pixel près, gestion des fenêtres, OCR, recherche de templates visuels, enregistrement vidéo et automatisation web.

---

## ✨ Points Forts & Fonctionnalités

- ⚡ **Ultra-léger et économe en ressources** : Fonctionne avec moins de 50 Mo de RAM, optimisé pour les processeurs dual-core et machines à ressources limitées.
- 🎯 **21 Outils MCP Tout-en-Un** : Aucun micro-serveur dispersé, une seule connexion stdio gère l'intégralité du cycle GUI.
- 📐 **Grille de repérage cartésien** : Ajout à la volée d'une grille millimétrée avec pas et sous-grilles configurables pour fiabiliser le ciblage spatial des LLMs.
- 🛡️ **Résilience XWayland / X11** : Stratégie de capture hybride (MSS + fallback Spectacle/Scrot) évitant les framebuffers noirs sous KDE/GNOME Wayland.
- 🔒 **Conception Zero-Slop** : Typage statique strict, aucun `shell=True` non sécurisé, gestion propre des descripteurs de fichiers et processus.

---

## 🛠️ Prérequis Système Linux

Le serveur s'appuie sur les utilitaires système standard Linux :

```bash
# Debian / Ubuntu / Linux Mint
sudo apt-get update && sudo apt-get install -y \
  xdotool wmctrl spectacle ffmpeg xclip tesseract-ocr libgl1

# Fedora / RHEL
sudo dnf install -y \
  xdotool wmctrl spectacle ffmpeg xclip tesseract libglvnd-glx

# Arch Linux / Manjaro
sudo pacman -S --needed \
  xdotool wmctrl spectacle ffmpeg xclip tesseract
```

---

## 🚀 Installation

> Pour le guide d'installation complet, le dépannage pas-à-pas et la configuration des clients MCP sur **Windows 10/11** et **Linux / macOS**, consultez le [**Guide d'Installation Détaillé (`INSTALL.md`)**](INSTALL.md).

### Méthode 1 : Script d'installation automatisé (Recommandé)

#### 🐧 Sur Linux (Bash) :
```bash
# En une seule ligne
curl -fsSL https://raw.githubusercontent.com/leandre755/gui_agent/main/install.sh | bash

# Ou en local depuis le dépôt
./install.sh
```

#### 🪟 Sur Microsoft Windows (PowerShell) :
```powershell
# En une seule ligne (PowerShell)
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/leandre755/gui_agent/main/install.ps1 | iex"

# Ou en local depuis le dépôt
.\install.ps1 -Local
```

### Méthode 2 : Installation isolée via `uv tool`

```bash
# Installation directe depuis PyPI (Linux / Windows)
uv tool install gui-agent

# Ou mise à jour
uv tool upgrade gui-agent
```

### Méthode 3 : Installation via `pip`

```bash
pip install gui-agent
```

---

## 🔌 Configuration des Clients MCP

### 1. Claude Code CLI

Ajoutez le serveur en une commande :

```bash
# Si installé via uv tool
claude mcp add gui-agent -- gui-agent

# Ou directement via uvx (sans installation préalable)
claude mcp add gui-agent -- uvx --from gui-agent gui-agent
```

### 2. Antigravity CLI (`~/.gemini/config/mcp_config.json`)

Ajoutez l'entrée suivante dans votre configuration globale MCP :

```json
{
  "mcpServers": {
    "gui-agent": {
      "command": "gui-agent",
      "args": [],
      "env": {
        "DISPLAY": ":0"
      }
    }
  }
}
```

*(Note : vous pouvez également utiliser la commande alias `mcp-gui-server`)*.

### 3. Cursor / VSCode (`mcp.json`)

```json
{
  "mcpServers": {
    "gui-agent": {
      "command": "uvx",
      "args": ["--from", "gui-agent", "gui-agent"]
    }
  }
}
```

---

## 🧭 Outils MCP Disponibles (21 Tools)

| Outil MCP | Description |
| :--- | :--- |
| `gui_get_screen_info` | Résolution de l'écran principal, position du curseur et dimensions. |
| `gui_take_screenshot` | Capture d'écran avec ou sans grille de coordonnées et sous-grilles. |
| `gui_mouse_move` | Déplacement fluide du curseur de la souris vers `(x, y)`. |
| `gui_mouse_click` | Clic (gauche, droit, milieu, double-clic) avec coordonnées optionnelles. |
| `gui_mouse_drag` | Glisser-déposer (drag & drop) d'un point initial vers un point cible. |
| `gui_mouse_scroll` | Défilement vertical ou horizontal (molette). |
| `gui_keyboard_type` | Saisie de texte avec intervalle configurable entre les frappes. |
| `gui_keyboard_press` | Frappe d'une touche spéciale ou combinaison (`ctrl+c`, `super`, `alt+tab`). |
| `gui_clipboard_get` | Lecture du contenu textuel du presse-papiers X11. |
| `gui_clipboard_set` | Écriture d'un texte dans le presse-papiers X11. |
| `gui_window_list` | Liste exhaustive des fenêtres actives avec IDs et titres (`wmctrl`). |
| `gui_window_focus` | Activation et mise au premier plan d'une fenêtre cible. |
| `gui_window_resize_move` | Déplacement et redimensionnement précis d'une fenêtre. |
| `gui_window_close` | Fermeture ordonnée d'une fenêtre par son identifiant. |
| `gui_app_launch` | Lancement asynchrone d'une application système en tâche de fond. |
| `gui_find_template` | Recherche d'un motif ou d'une image modèle par template matching OpenCV. |
| `gui_find_text` | Détection et localisation spatiale de texte à l'écran via OCR (Tesseract / RapidOCR). |
| `gui_click_text` | Détection OCR et clic automatique centré sur la première occurrence d'un texte. |
| `gui_web_action` | Navigation et interaction web headless ou visible via Playwright. |
| `gui_start_video_recording` | Démarrage d'un enregistrement vidéo de l'écran via FFmpeg (X11grab). |
| `gui_stop_video_recording` | Arrêt propre et finalisation du flux vidéo FFmpeg. |

---

## ⚙️ Variables d'Environnement

| Variable | Description | Valeur par défaut |
| :--- | :--- | :--- |
| `DISPLAY` | Serveur d'affichage X11 cible | `:0` |
| `GUI_AGENT_SCREENSHOTS_DIR` | Répertoire de sauvegarde des captures d'écran | `~/.local/share/gui-agent/screenshots` |

---

## 🗑️ Désinstallation Propre

Pour supprimer complètement `gui-agent`, ses environnements isolés et nettoyer les configurations MCP :

### 🐧 Sur Linux / macOS (Bash) :
```bash
# Désinstallation automatisée et nettoyage MCP
curl -fsSL https://raw.githubusercontent.com/leandre755/gui_agent/main/uninstall.sh | bash

# Ou en local avec purge des captures d'écran :
./uninstall.sh --purge-data --yes
```

### 🪟 Sur Microsoft Windows (PowerShell) :
```powershell
# Désinstallation automatisée et nettoyage MCP
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/leandre755/gui_agent/main/uninstall.ps1 | iex"

# Ou en local avec purge des captures d'écran :
.\uninstall.ps1 -PurgeData -Yes
```

---

## 🧪 Développement & Tests

```bash
# Cloner le dépôt
git clone https://github.com/leandre755/gui_agent.git
cd gui_agent

# Créer l'environnement virtuel avec UV
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Exécuter les tests unitaires
pytest

# Exécuter les vérifications de conformité Zero-Slop
ALLOW_CONFIG_EDIT=1 ./.githooks/pre-commit
```

---

## 📄 Licence

Ce projet est distribué sous licence [MIT](LICENSE).
