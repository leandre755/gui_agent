<p align="center">
  <img src="https://files.catbox.moe/udf9j4.jpeg" alt="gui-agent Hero Banner" width="100%" style="border-radius: 8px;" />
</p>

<h1 align="center"><img src="https://files.catbox.moe/xei715.png" alt="gui-agent Logo" height="42" style="vertical-align: middle; margin-right: 10px;" />gui-agent</h1>

<p align="center"><b>Serveur FastMCP Monolithique pour le Contrôle Graphique (Computer Use) sous Linux et Windows</b></p>

<p align="center">🌐 <b><a href="README.md">English</a></b> | <b><a href="README.fr.md">Français</a></b></p>

<p align="center">
  <a href="#-fonctionnalités-principales"><img src="https://img.shields.io/badge/Fonctionnalit%C3%A9s-→-10B981?style=flat-square" alt="Fonctionnalités" /></a>
  <a href="#-architecture--flux-de-fonctionnement"><img src="https://img.shields.io/badge/Architecture-→-10B981?style=flat-square" alt="Architecture" /></a>
  <a href="#-installation"><img src="https://img.shields.io/badge/Installation-→-10B981?style=flat-square" alt="Installation" /></a>
  <a href="#-configuration-des-clients-mcp"><img src="https://img.shields.io/badge/Clients_MCP-→-10B981?style=flat-square" alt="Clients MCP" /></a>
  <a href="#-référence-du-toolset--cli"><img src="https://img.shields.io/badge/Toolset-→-10B981?style=flat-square" alt="Toolset" /></a>
  <a href="#-désinstallation-propre"><img src="https://img.shields.io/badge/D%C3%A9sinstallation-→-10B981?style=flat-square" alt="Désinstallation" /></a>
  <a href="#-développement--quality-gate"><img src="https://img.shields.io/badge/D%C3%A9veloppement-→-10B981?style=flat-square" alt="Développement" /></a>
</p>

<p align="center">
  <a href="https://github.com/leandre755/gui_agent/releases/tag/v0.1.0"><img src="https://img.shields.io/badge/version-0.1.0-3FB950?style=flat-square" alt="Version 0.1.0" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-34D399?style=flat-square" alt="Python 3.10+" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/licence-MIT-F0883E?style=flat-square" alt="Licence MIT" /></a>
  <a href="#"><img src="https://img.shields.io/badge/plateforme-Linux%20%7C%20Windows-10B981?style=flat-square" alt="Plateforme Linux | Windows" /></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/Protocole_MCP-1.2.0+-10B981?style=flat-square" alt="Protocole MCP 1.2.0+" /></a>
  <a href="https://github.com/leandre755/gui_agent/discussions"><img src="https://img.shields.io/badge/Discussions-Q%26A-blue?style=flat-square" alt="Discussions Q&A" /></a>
</p>

### La Philosophie : Pourquoi gui-agent ?

Les agents IA autonomes interagissant avec les interfaces graphiques modernes sont fréquemment entravés par des architectures fragmentées, une latence critique et des boucles de vision fragiles. Les dispositifs d'automatisation traditionnels contraignent les modèles à percevoir le système d'exploitation exclusivement à travers des captures matricielles répétitives, générant des temps d'aller-retour (RTT) prohibitifs de 2 à 5 secondes par action motrice. Ce réductionnisme engendre des décalages spatiaux sous mise à l'échelle fractionnelle, perd les composants évanescents et sature les contextes d'images redondantes.

**gui-agent** redéfinit le contrôle graphique en alignant les décisions de l'agent sur l'ontologie réelle des systèmes d'exploitation : processus structurés en RAM, arbres d'accessibilité (AT-SPI2 / D-Bus), compositeurs de fenêtres (X11 / Wayland) et sous-systèmes d'événements du noyau (`uinput`, `evdev`). Fondé sur deux piliers indissociables — **l'Escalade Progressive (L3/L2/L1)** et le **Moteur REPL Local CodeAct** —, le serveur permet aux modèles d'agir en RAM en moins de 50 ms via la médiation native Rust (`gui-agent-atspi`), de basculer sur l'OCR local ou la grille cartésienne calibrée, et d'exécuter des séquences d'actions complexes localement en mémoire hôte en moins de 5 ms.

Fonctionnant via une unique connexion FastMCP résiliente sur l'entrée/sortie standard (stdio), **gui-agent** maintient une empreinte mémoire de base inférieure à 50 Mo de RAM, garantissant la réactivité sur processeurs double-cœur sans dépendance de vision cloud ni démon persistant superflu. Les implémentations de plateforme sont isolées dans des répertoires étanches à la racine (`linux/`, `windows/`, `macos/`) avec résolution dynamique des chemins XDG, aucun chemin utilisateur en dur, et la préservation intégrale de l'enregistrement vidéo continu (`gui_start_video_recording`, `gui_stop_video_recording`) pour l'audit déterministe.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Activities/Bullseye.png" alt="Bullseye" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Fonctionnalités Principales

Le serveur expose 21 outils FastMCP monolithiques couvrant l'intégralité du cycle de vie du contrôle graphique (Computer Use) du système d'exploitation. Tous les outils fonctionnent via un unique canal de communication standard d'entrée/sortie (stdio) JSON-RPC 2.0.

| Nom de l'Outil | Domaine | Description | État |
| :--- | :--- | :--- | :--- |
| `gui_get_screen_info` | <img src="https://img.shields.io/badge/%C3%89cran-10B981?style=flat-square" alt="Écran" /> | Récupère la résolution d'écran, les moniteurs détectés, les coordonnées d'affichage et l'état failsafe. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_take_screenshot` | <img src="https://img.shields.io/badge/%C3%89cran-10B981?style=flat-square" alt="Écran" /> | Capture l'affichage du bureau complet ou rogné avec incrustation d'une grille cartésienne dynamique. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_mouse_move` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Déplace de manière fluide le curseur vers des coordonnées absolues `(x, y)` ou normalisées `[0, 1000]`. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_mouse_click` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Envoie des clics de souris simples, doubles ou triples (`left`, `right`, `middle`) aux coordonnées cibles. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_mouse_drag` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Exécute des opérations de glisser-déposer fluides de `(x1, y1)` vers `(x2, y2)` avec durée paramétrable. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_mouse_scroll` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Simule des actions de molette directionnelles (`up`, `down`, `left`, `right`) avec pas ajustable. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_keyboard_type` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Saisit du texte caractère par caractère avec micro-délais réalistes pour prévenir les blocages anti-bot. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_keyboard_press` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Émet des codes de touches spécialisés et combinaisons de raccourcis complexes (`ctrl+c`, `super`, `alt+tab`, `Return`). | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_clipboard_get` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Lit le texte du presse-papiers OS avec bascule multi-backend automatisée (`pyperclip`, `xclip`, `xsel`). | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_clipboard_set` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Écrit du texte arbitraire dans le presse-papiers système avec synchronisation multi-backend. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_window_list` | <img src="https://img.shields.io/badge/Fen%C3%AAtre-10B981?style=flat-square" alt="Fenêtre" /> | Inspecte la hiérarchie des fenêtres actives, renvoyant IDs de fenêtre, PIDs, titres et classes WM. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_window_focus` | <img src="https://img.shields.io/badge/Fen%C3%AAtre-10B981?style=flat-square" alt="Fenêtre" /> | Active et place une fenêtre d'application cible au premier plan du bureau via son identifiant. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_window_resize_move` | <img src="https://img.shields.io/badge/Fen%C3%AAtre-10B981?style=flat-square" alt="Fenêtre" /> | Déplace et redimensionne une fenêtre cible avec des paramètres de coordonnées et dimensions exacts. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_window_close` | <img src="https://img.shields.io/badge/Fen%C3%AAtre-10B981?style=flat-square" alt="Fenêtre" /> | Ferme proprement une fenêtre d'application ouverte via les protocoles natifs du gestionnaire de fenêtres. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_app_launch` | <img src="https://img.shields.io/badge/Fen%C3%AAtre-10B981?style=flat-square" alt="Fenêtre" /> | Lance des applications système sous forme de processus asynchrones en arrière-plan ou synchrones. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_find_template` | <img src="https://img.shields.io/badge/Vision-34D399?style=flat-square" alt="Vision" /> | Recherche des sous-images sur l'écran par corrélation croisée normalisée via OpenCV. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_find_text` | <img src="https://img.shields.io/badge/Vision-34D399?style=flat-square" alt="Vision" /> | Identifie et localise les coordonnées de texte à l'écran via des moteurs OCR (Tesseract / RapidOCR). | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_click_text` | <img src="https://img.shields.io/badge/Vision-34D399?style=flat-square" alt="Vision" /> | Effectue une recherche OCR complète et clique immédiatement au centre du cadre englobant le texte. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_web_action` | <img src="https://img.shields.io/badge/Web-34D399?style=flat-square" alt="Web" /> | Exécute des interactions web déterministes (`aria_tree`, `click`, `type`, `screenshot`) via Playwright. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_start_video_recording` | <img src="https://img.shields.io/badge/M%C3%A9dia-F0883E?style=flat-square" alt="Média" /> | Démarre un enregistrement vidéo d'écran en arrière-plan à faible surcharge via FFmpeg (`x11grab` / H.264). | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_stop_video_recording` | <img src="https://img.shields.io/badge/M%C3%A9dia-F0883E?style=flat-square" alt="Média" /> | Arrête proprement l'enregistrement FFmpeg actif, vide le conteneur MP4 et évite les fuites de descripteurs. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Gear.png" alt="Gear" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Architecture & Flux de Fonctionnement

**gui-agent** fonctionne comme une passerelle en boucle fermée pour le Computer Use entre les modèles de raisonnement LLM et le système d'exploitation hôte, combinant actuation sémantique en RAM, scripts locaux et rétroaction motrice.

<p align="center">
  <img src="https://gist.githubusercontent.com/personnal-agent/f0b933b981a70de123282eb99fd6df44/raw/exc-how-it-works-fr.svg" alt="Architecture & Flux gui-agent" width="100%" style="border-radius: 10px;" />
</p>

### Pipeline d'Exécution Technique & Piliers Fondateurs

1. **Pilier 1 : Escalade Progressive & Actionnement par Paliers** : Au lieu d'imposer un mode d'action unique, l'architecture priorise l'efficience cognitive et d'exécution à travers des paliers étagés : le Niveau L3 interagit avec l'arbre d'accessibilité (AT-SPI2 / D-Bus via le médiateur Rust compilé `gui-agent-atspi`) directement en RAM pour une actuation déterministe en moins de 50 ms sans jeton d'image ; le Niveau L2 exploite un OCR local découplé (RapidOCR/Tesseract) sans surcoût d'inférence ; le Niveau L1 offre le filet de sécurité matériel ultime via grille cartésienne calibrée et dispatchers d'entrée natifs (l'intégration noyau directe `uinput`/`evdev` étant inscrite sur la feuille de route) ; et un shell PTY interactif gère les commandes privilégiées.
2. **Pilier 2 : Architecture d'Exécution Haute Efficacité** : Afin d'éliminer la latence réseau des allers-retours (RTT) successifs, l'architecture conçoit un environnement d'exécution local isolé (`execute_script` via `core/repl.py`). Les modèles y projetteront directement leur logique d'inspection et d'action sous forme de code Python exécuté en mémoire hôte via le SDK unifié `mcp_core`. Les vérifications conditionnelles, calculs cinématiques de glisser et scrutations dynamiques se résoudront en un unique aller-retour cognitif à moins de 5 ms avec moins de 15 Mo de RAM (planifié dans la feuille de route Phase 2).
3. **Acquisition d'Écran Ultra-Rapide & Incrustation de Grille Cartésienne** : Lorsqu'un agent demande l'état visuel via `gui_take_screenshot`, le serveur capture le framebuffer brut via MSS avec bascule automatique sur KDE Spectacle ou Scrot sous XWayland. Le moteur superpose une grille cartésienne millimétrique à contraste adaptatif à intervalles configurables (ex. 100px), permettant aux modèles de déduire les coordonnées cibles avec certitude mathématique.
4. **Moteur Double de Normalisation des Coordonnées** : Le serveur accepte les coordonnées en pixels physiques absolus `(x, y)` ou en ratios normalisés `[0, 1000]` sur toute géométrie d'affichage ou configuration multi-écrans. Un convertisseur automatique gère le bornage aux limites, la mise à l'échelle DPI et la translation spatiale de manière transparente.
5. **Répartiteur d'Entrées et de Fenêtres OS Natif** : Les frappes, raccourcis, clics et glissers sont acheminés via des pilotes natifs à faible latence (`xdotool` et `python-xlib` sous Linux, API Win32 sous Windows). Des micro-délais humanisés émulent une interaction naturelle. Les commandes de gestion de fenêtres (`wmctrl` / `xprop`) inspectent et manipulent l'état des fenêtres sans verrouiller le gestionnaire de fenêtres.
6. **Vision Locale, OCR & Automatisation Playwright** : La correspondance de motifs (`cv2.matchTemplate`) permet une détection robuste des icônes malgré les variations de thèmes. La détection de texte combine Tesseract OCR avec le repli ONNX RapidOCR. L'automatisation web s'appuie sur Playwright pour inspecter les arbres ARIA et manipuler directement les nœuds DOM sans ambiguïté visuelle.

### Architecture Multi-Plateforme à la Racine & Résolution Dynamique des Chemins

Le projet structure les implémentations par système d'exploitation dans des répertoires dédiés à la racine sans aucun chemin en dur :
- **`linux/`** : Implémentation Linux complète intégrant le serveur (`server.py`), le médiateur natif Rust AT-SPI2 / D-Bus (`linux/crates/atspi_mediator` compilé en `gui-agent-atspi`), les scripts d'installation/désinstallation (`install.sh`, `uninstall.sh`), les tests et exemples, et la résolution dynamique des chemins XDG (`paths.py`).
- **`windows/`** : Répertoire Windows dédié (`install.ps1`, `uninstall.ps1`, backend natif UI Automation en cours de développement).
- **`macos/`** : Répertoire macOS dédié réservé pour les futures implémentations NSAccessibility et Quartz Event Taps.
Tous les chemins d'exécution — incluant les captures d'écran (`$XDG_CACHE_HOME/gui-agent/screenshots` ou `GUI_AGENT_SCREENSHOTS_DIR`), les vidéos continues (`$XDG_CACHE_HOME/gui-agent/videos` ou `GUI_AGENT_VIDEOS_DIR`) et les données (`$XDG_DATA_HOME/gui-agent`) — sont résolus dynamiquement à l'exécution.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Package.png" alt="Package" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Installation

> Pour les instructions détaillées par OS, les matrices de dépannage et les configurations hors-ligne, consultez le [**Guide d'Installation Détaillé (INSTALL.md)**](INSTALL.md).

### 1. Installation Automatisée (Recommandée)

#### Linux (Bash)
Exécutez le script d'installation automatisé pour vérifier les dépendances, installer Astral uv, compiler le médiateur Rust et enregistrer le serveur MCP :

```bash
# Téléchargement et exécution de l'installateur automatisé via curl
curl -fsSL https://raw.githubusercontent.com/leandre755/gui_agent/v0.1.0/linux/install.sh | bash

# Ou exécuter localement depuis un dépôt cloné
./linux/install.sh
```

#### Microsoft Windows (PowerShell)
Lancez PowerShell (utilisateur standard ou administrateur) et exécutez le script d'installation automatisé :

```powershell
# Téléchargement et exécution du script d'installation
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/leandre755/gui_agent/v0.1.0/windows/install.ps1" -OutFile "install.ps1"
powershell -ExecutionPolicy Bypass -File .\install.ps1

# Ou exécuter localement depuis un dépôt cloné
.\windows\install.ps1 -Local
```

### 2. Déploiement Isolé via uv tool
Installez gui-agent directement dans un environnement isolé avec des points d'entrée CLI globaux :

```bash
# Installer depuis PyPI
uv tool install gui-agent

# Ou installer depuis le dépôt GitHub
uv tool install "git+https://github.com/leandre755/gui_agent.git"

# Mettre à niveau vers la dernière version
uv tool upgrade gui-agent
```

### 3. Prérequis Système Linux
Sous Linux, installez les bibliothèques natives de gestion de fenêtres, OCR, multimédia, accessibilité AT-SPI et Rust :

```bash
# Debian / Ubuntu / Linux Mint
sudo apt-get update && sudo apt-get install -y \
  xdotool wmctrl spectacle ffmpeg xclip tesseract-ocr libgl1 libatspi-dev cargo rustc

# Fedora / RHEL
sudo dnf install -y \
  xdotool wmctrl spectacle ffmpeg xclip tesseract libglvnd-glx at-spi2-core-devel cargo rust

# Arch Linux / Manjaro
sudo pacman -S --needed \
  xdotool wmctrl spectacle ffmpeg xclip tesseract at-spi2-core cargo rust
```

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Electric%20Plug.png" alt="Plug" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Configuration des Clients MCP

### 1. Claude Code CLI
Enregistrez le serveur dans Claude Code CLI en une seule commande :

```bash
# Si installé via uv tool
claude mcp add gui-agent -- gui-agent

# Exécution directe à la volée via uvx (zéro pré-installation requise)
claude mcp add gui-agent -- uvx --from gui-agent gui-agent
```

### 2. Antigravity CLI
Ajoutez la définition du serveur à votre configuration MCP globale Antigravity :

- **Linux / macOS** : `~/.gemini/config/mcp_config.json`
- **Windows** : `%USERPROFILE%\.gemini\config\mcp_config.json`

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

*(Remarque : L'exécutable alias `mcp-gui-server` peut également être utilisé comme cible `command`).*

### 3. Cursor & VSCode
Ajoutez l'entrée suivante dans votre fichier `mcp.json` de Cursor (`~/.cursor/mcp.json` ou `.vscode/mcp.json`) :

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

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Hammer%20and%20Wrench.png" alt="Tools" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Référence du Toolset & CLI

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Computer%20Mouse.png" alt="Mouse" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Outils d'Affichage & Curseur (10 outils)</b></summary>

#### `gui_get_screen_info`
Récupère les paramètres d'affichage, les topologies d'écrans, la résolution active et les variables de session.
- **Paramètres** : Aucun.
- **Retourne** : `dict` contenant `resolution`, `width`, `height`, la liste `monitors`, `display_env` et `failsafe_enabled`.

#### `gui_take_screenshot`
Capture des images plein écran ou rognées avec incrustation optionnelle d'une grille cartésienne.
- **Paramètres** :
  - `monitor_index` (`int`, valeur par défaut `1`) : Index du moniteur cible (`0` pour le canevas virtuel).
  - `crop_box` (`list[int] | None`, valeur par défaut `None`) : Sous-région `[x, y, width, height]`.
  - `apply_grid` (`bool`, valeur par défaut `True`) : Incruste la grille de coordonnées cartésiennes.
  - `grid_interval` (`int`, valeur par défaut `100`) : Intervalle en pixels entre les lignes de grille (minimum 20).
  - `format` (`str`, valeur par défaut `"png"`) : Format de l'image de sortie (`"png"` ou `"jpeg"`).
  - `quality` (`int`, valeur par défaut `80`) : Qualité de compression (1-100) pour la sortie JPEG.
  - `output_path` (`str | None`, valeur par défaut `None`) : Chemin du fichier de destination. Les chemins relatifs sont résolus en chemins absolus et les dossiers parents manquants sont créés. Les chemins vides et les répertoires existants sont rejetés. Si le chemin n'a pas d'extension, l'extension correspondant à `format` est automatiquement ajoutée. Une extension incompatible est rejetée. Si le fichier existe déjà, une réservation atomique et l'ajout de suffixes incrémentaux tels que `(1)` et `(2)` protègent le fichier existant contre l'écrasement. `screenshot_path` contient le chemin absolu effectivement utilisé. Par défaut : image horodatée dans le dossier des captures.
  - `include_base64` (`bool`, valeur par défaut `False`) : Renvoie la représentation textuelle encodée en Base64.
- **Retourne** : `dict` contenant `screenshot_path` (chemin absolu résolu), `raw_screenshot_path`, `format`, `resolution`, `cropped`, `grid_applied`, `grid_interval`, `renamed_due_to_conflict`, `message` et `base64_data` (présent lorsque `include_base64` est activé).

#### `gui_mouse_move`
Déplace de manière fluide le curseur de la souris vers les coordonnées cibles.
- **Paramètres** :
  - `x` (`float`) : Position X cible.
  - `y` (`float`) : Position Y cible.
  - `duration` (`float`, valeur par défaut `0.2`) : Durée d'interpolation du mouvement en secondes.
  - `normalized` (`bool`, valeur par défaut `False`) : Définir à `True` lors de l'utilisation de coordonnées `[0, 1000]`.
  - `monitor_index` (`int`, valeur par défaut `1`) : Moniteur de référence pour les calculs de coordonnées.

#### `gui_mouse_click`
Exécute des clics simples, doubles ou multiples à des coordonnées spécifiques.
- **Paramètres** :
  - `x` (`float`) : Position X cible.
  - `y` (`float`) : Position Y cible.
  - `button` (`str`, valeur par défaut `"left"`) : Bouton de souris (`"left"`, `"right"`, `"middle"`).
  - `clicks` (`int`, valeur par défaut `1`) : Nombre de clics à exécuter.
  - `normalized` (`bool`, valeur par défaut `False`) : Définir à `True` pour les coordonnées `[0, 1000]`.
  - `monitor_index` (`int`, valeur par défaut `1`) : Moniteur de référence.

#### `gui_mouse_drag`
Exécute un mouvement de glisser-déposer fluide entre deux positions spatiales.
- **Paramètres** :
  - `x1` (`float`) : Position X de départ.
  - `y1` (`float`) : Position Y de départ.
  - `x2` (`float`) : Position X d'arrivée.
  - `y2` (`float`) : Position Y d'arrivée.
  - `duration` (`float`, valeur par défaut `0.5`) : Durée de l'animation de glissement en secondes.
  - `normalized` (`bool`, valeur par défaut `False`) : Définir à `True` pour les coordonnées `[0, 1000]`.
  - `monitor_index` (`int`, valeur par défaut `1`) : Moniteur de référence.

#### `gui_mouse_scroll`
Simule le défilement de la molette de souris le long des axes verticaux ou horizontaux.
- **Paramètres** :
  - `clicks` (`int`) : Nombre de crans de défilement (entier positif).
  - `direction` (`str`, valeur par défaut `"down"`) : Direction (`"up"`, `"down"`, `"left"`, `"right"`).

#### `gui_keyboard_type`
Saisit du texte séquentiellement avec des variations temporelles réalistes de frappe humaine.
- **Paramètres** :
  - `text` (`str`) : Contenu textuel à saisir.
  - `delay` (`float`, valeur par défaut `0.06`) : Délai de base entre les frappes de touches en secondes.

#### `gui_keyboard_press`
Simule des pressions de touches individuelles ou des combinaisons de raccourcis complexes.
- **Paramètres** :
  - `key` (`str`) : Identifiant de touche ou accord (ex. `"Return"`, `"Escape"`, `"ctrl+c"`, `"alt+tab"`, `"super"`).

#### `gui_clipboard_get`
Lit le contenu textuel actuel du presse-papiers système.
- **Paramètres** : Aucun.
- **Retourne** : `dict` contenant le `text` du presse-papiers, la longueur `length` et la méthode `method` d'extraction.

#### `gui_clipboard_set`
Écrit du contenu textuel dans le presse-papiers du système d'exploitation.
- **Paramètres** :
  - `text` (`str`) : Contenu textuel à stocker dans le presse-papiers.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Window.png" alt="Window" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Contrôle des Fenêtres & Processus (5 outils)</b></summary>

#### `gui_window_list`
Énumère toutes les fenêtres actives du bureau avec leurs métadonnées.
- **Paramètres** : Aucun.
- **Retourne** : `dict` avec tableau `windows` contenant l'`id`, `title`, `pid` et `wm_class` de chaque fenêtre.

#### `gui_window_focus`
Active et place la fenêtre spécifiée au premier plan.
- **Paramètres** :
  - `window_id` (`int`) : Identifiant numérique de fenêtre obtenu via `gui_window_list`.

#### `gui_window_resize_move`
Repositionne et redimensionne une fenêtre d'application en une seule opération atomique.
- **Paramètres** :
  - `window_id` (`int`) : Identifiant numérique de la fenêtre cible.
  - `x` (`int`) : Nouvelle coordonnée X du coin supérieur gauche.
  - `y` (`int`) : Nouvelle coordonnée Y du coin supérieur gauche.
  - `width` (`int`) : Nouvelle largeur de la fenêtre en pixels.
  - `height` (`int`) : Nouvelle hauteur de la fenêtre en pixels.

#### `gui_window_close`
Envoie une requête de fermeture ordonnée à une fenêtre cible.
- **Paramètres** :
  - `window_id` (`int`) : Identifiant numérique de la fenêtre cible.

#### `gui_app_launch`
Lance un processus ou exécutable du système d'exploitation.
- **Paramètres** :
  - `command` (`str`) : Ligne de commande shell ou chemin de l'exécutable à lancer.
  - `background` (`bool`, valeur par défaut `True`) : Exécuter de manière détachée en tâche de fond (`True`) ou synchrone (`False`).

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Magnifying%20Glass%20Tilted%20Left.png" alt="Search" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Vision & Automatisation OCR (3 outils)</b></summary>

#### `gui_find_template`
Effectue une recherche de motif normalisée via OpenCV pour localiser des éléments graphiques.
- **Paramètres** :
  - `template_path` (`str`) : Chemin vers le fichier de l'image modèle de référence.
  - `threshold` (`float`, valeur par défaut `0.8`) : Seuil de confiance (entre 0.01 et 1.0).
  - `monitor_index` (`int`, valeur par défaut `1`) : Index du moniteur à inspecter.
- **Retourne** : `dict` contenant les coordonnées du centre détecté `(x, y)` et le score `confidence`.

#### `gui_find_text`
Extrait les boîtes englobantes de texte par OCR (Tesseract / RapidOCR) et calcule les coordonnées centroïdes.
- **Paramètres** :
  - `text` (`str`) : Chaîne de caractères cible à découvrir.
  - `confidence` (`float`, valeur par défaut `0.6`) : Score minimal de confiance OCR (0.0 à 1.0).
  - `monitor_index` (`int`, valeur par défaut `1`) : Index du moniteur où effectuer la recherche.
- **Retourne** : `dict` contenant `text_found`, le centroïde `(x, y)`, `confidence` et la boîte englobante `[x, y, w, h]`.

#### `gui_click_text`
Exécute une recherche OCR et envoie un clic de souris directement au centre du texte découvert.
- **Paramètres** :
  - `text` (`str`) : Chaîne de texte cible à localiser et cliquer.
  - `button` (`str`, valeur par défaut `"left"`) : Bouton de souris à actionner (`"left"`, `"right"`, `"middle"`).
  - `clicks` (`int`, valeur par défaut `1`) : Nombre de clics à effectuer.
  - `monitor_index` (`int`, valeur par défaut `1`) : Moniteur cible.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Movie%20Camera.png" alt="Camera" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Web & Enregistrement Multimédia (3 outils)</b></summary>

#### `gui_web_action`
Interagit directement avec les pages web via Chromium headless propulsé par Playwright.
- **Paramètres** :
  - `url` (`str`) : Adresse web ou URL de fichier local vers laquelle naviguer.
  - `action` (`str`, valeur par défaut `"aria_tree"`) : Action à exécuter (`"aria_tree"`, `"click"`, `"type"`, `"screenshot"`).
  - `selector` (`str | None`, valeur par défaut `None`) : Sélecteur CSS ou XPath pour les actions `click` et `type`.
  - `text` (`str | None`, valeur par défaut `None`) : Données textuelles à saisir lorsque `action="type"`.
  - `viewport_width` (`int`, valeur par défaut `1280`) : Largeur de fenêtre du navigateur.
  - `viewport_height` (`int`, valeur par défaut `720`) : Hauteur de fenêtre du navigateur.
  - `timeout_ms` (`int`, valeur par défaut `30000`) : Délai maximal de navigation et de localisation en millisecondes.

#### `gui_start_video_recording`
Lance un sous-processus asynchrone d'enregistrement d'écran via FFmpeg avec une surcharge CPU minimale.
- **Paramètres** :
  - `output_path` (`str | None`, valeur par défaut `None`) : Chemin du fichier de destination (défaut : MP4 horodaté dans le dossier des vidéos).
  - `fps` (`int`, valeur par défaut `5`) : Cadence de capture vidéo (1 à 30 IPS).
  - `monitor_index` (`int`, valeur par défaut `1`) : Index du moniteur cible.
  - `duration` (`int | None`, valeur par défaut `None`) : Limite optionnelle de durée automatique en secondes.

#### `gui_stop_video_recording`
Arrête proprement l'enregistrement FFmpeg en cours et valide le conteneur du fichier MP4 généré.
- **Paramètres** : Aucun.
- **Retourne** : `dict` contenant `output_path`, `file_exists` et `file_size_bytes`.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Control%20Knobs.png" alt="Config" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Variables d'Environnement (Configuration)</b></summary>

| Variable | Description | Valeur par Défaut |
| :--- | :--- | :--- |
| `DISPLAY` | Identifiant du serveur d'affichage X11 cible. | `:0` |
| `GUI_AGENT_SCREENSHOTS_DIR` | Répertoire où sont enregistrées les captures et découpes d'écran. | `$XDG_CACHE_HOME/gui-agent/screenshots` |
| `GUI_AGENT_VIDEOS_DIR` | Répertoire où sont sauvegardés les enregistrements vidéo MP4 continus. | `$XDG_CACHE_HOME/gui-agent/videos` |
| `GUI_AGENT_ATSPI_BIN` | Chemin d'accès personnalisé vers le binaire natif Rust `gui-agent-atspi`. | Découverte automatique |

</details>

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Wastebasket.png" alt="Trash" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Désinstallation Propre

Pour purger proprement `gui-agent`, supprimer les environnements isolés et retirer les configurations MCP enregistrées :

### 1. Linux (Bash)

```bash
# Téléchargement et exécution du désinstallateur automatisé
curl -fsSLO https://raw.githubusercontent.com/leandre755/gui_agent/v0.1.0/linux/uninstall.sh
chmod +x uninstall.sh && ./uninstall.sh --purge-data --yes

# Ou désinstallation locale avec purge complète des données et caches
./linux/uninstall.sh --purge-data --yes
```

### 2. Microsoft Windows (PowerShell)

```powershell
# Téléchargement et exécution du désinstallateur automatisé
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/leandre755/gui_agent/v0.1.0/windows/uninstall.ps1" -OutFile "uninstall.ps1"
powershell -ExecutionPolicy Bypass -File .\uninstall.ps1 -PurgeData -Yes

# Ou désinstallation locale avec purge complète des données et caches
.\windows\uninstall.ps1 -PurgeData -Yes
```

#### Éléments nettoyés par le désinstallateur :
- Supprime les binaires `gui-agent`, `mcp-gui-server` et `gui-agent-atspi` des chemins standards (`~/.local/bin` ou virtualenv).
- Désenregistre le serveur MCP de la configuration du CLI Claude Code.
- Nettoie les entrées JSON du fichier `mcp_config.json` d'Antigravity.
- Purge les dossiers d'exécution et supprime optionnellement captures et enregistrements (`--purge-data` / `-PurgeData`).

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Shield.png" alt="Shield" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Développement & Quality-Gate

Le projet applique des normes d'ingénierie logicielle strictes, vérifiées par un pipeline de 8 couches de hooks pre-commit (Quality-Gate) et une couverture de tests complète.

### 1. Configuration de l'Environnement Local

```bash
# Cloner le dépôt
git clone https://github.com/leandre755/gui_agent.git
cd gui_agent

# Initialiser l'environnement virtuel avec Astral UV
uv venv
source .venv/bin/activate

# Installer le paquet en mode éditable avec dépendances de développement et compiler les extensions Rust (requiert Cargo)
uv pip install -e ".[dev]"
```

### 2. Exécution des Suites de Tests

```bash
# Exécuter les tests unitaires et d'intégration à travers les couches de plateforme
pytest -v linux/tests/
```

### 3. Vérification Pre-Commit Quality-Gate en 8 Couches

Chaque commit est filtré par 8 couches strictes de validation statique pour éliminer la dette technique et les vulnérabilités de sécurité :

```bash
# Exécuter le hook de validation Quality-Gate en 8 couches localement
ALLOW_CONFIG_EDIT=1 ./.githooks/pre-commit
```

| Couche | Validateur | Périmètre & Invariants de Qualité Appliqués |
| :--- | :--- | :--- |
| 1 | `anti-leak` | Bloque les jetons secrets, clés privées et identifiants `.env` dans les fichiers indexés. |
| 2 | `pip-audit` | Audite l'arbre des dépendances Python contre les bases de vulnérabilités CVE connues. |
| 3 | `ruff check` | Impose zéro avertissement de lint, le respect de PEP 8 et les idiomes Python 3.10+ modernes. |
| 4 | `ruff format` | Vérifie le formatage déterministe et uniforme du code sur toutes les sources Python. |
| 5 | `mypy` | Vérification statique stricte des types sans aucune définition non typée autorisée. |
| 6 | `sonar/smells` | Contrôle la complexité cognitive (McCabe C90 <= 25), les risques de bugs et simplifications. |
| 7 | `bandit` | Analyse statique AST de sécurité prévenant les appels de sous-processus et motifs non sécurisés. |
| 8 | `semgrep` | Scanner de sécurité SAST détectant les risques d'injection de code et d'isolation système. |

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Scroll.png" alt="Scroll" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Licence

Ce projet est distribué sous les termes de la [Licence MIT](LICENSE).

Copyright (c) 2026 Leandre. Tous droits réservés.
