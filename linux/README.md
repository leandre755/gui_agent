# Plateforme Linux — FastMCP GUI Agent

Ce répertoire regroupe les composants natifs et l'outillage d'intégration spécifiques à **Linux** (X11 / XWayland / AT-SPI2).

---

## 1. Architecture des Modules Linux

- **`paths.py`** : Résolution dynamique des chemins système conforme aux spécifications **XDG Base Directory** :
  - Données : `$XDG_DATA_HOME/gui-agent` (défaut : `~/.local/share/gui-agent`)
  - Configuration : `$XDG_CONFIG_HOME/gui-agent` (défaut : `~/.config/gui-agent`)
  - Cache : `$XDG_CACHE_HOME/gui-agent` (défaut : `~/.cache/gui-agent`)
  - Captures d'écran : `$XDG_CACHE_HOME/gui-agent/screenshots` (ou `GUI_AGENT_SCREENSHOTS_DIR`)
  - Captures vidéo : `$XDG_CACHE_HOME/gui-agent/videos` (ou `GUI_AGENT_VIDEOS_DIR`)
  - Découverte dynamique de binaires natifs (`gui-agent-atspi`, `computer-use-linux`).
- **`accessibility.py`** : Médiation sémantique d'accessibilité programmatique via **AT-SPI2 / D-Bus** (`get_app_state`, `perform_action`, `set_value`).
- **`input.py`** : Émulation d'entrées clavier et souris (X11 / `uinput` / `evdev`).
- **`window.py`** : Ciblage et manipulation des fenêtres (EWMH, `wmctrl`, `xdotool`).

---

## 2. Scripts d'Installation et d'Automatisation

- **`install.sh`** : Détection des prérequis système (`xdotool`, `wmctrl`, `ffmpeg`, `libatspi`), configuration de l'environnement virtuel Python et compilation/installation du binaire natif Rust `gui-agent-atspi`.
- **`uninstall.sh`** : Nettoyage propre et déterministe des binaires autonomes et caches spécifiques.
