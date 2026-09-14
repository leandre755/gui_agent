<p align="center">
  <img src="https://files.catbox.moe/udf9j4.jpeg" alt="gui-agent Hero Banner" width="100%" style="border-radius: 8px;" />
</p>

<h1 align="center"><img src="https://files.catbox.moe/xei715.png" alt="gui-agent Logo" height="42" style="vertical-align: middle; margin-right: 10px;" />gui-agent</h1>

<p align="center"><b>Serveur FastMCP Unifié pour le Contrôle Graphique (Computer Use) sous Linux et Windows</b></p>

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

Le serveur expose 15 outils FastMCP unifiés structurés par couches opérationnelles, couvrant l'intégralité du cycle de vie du contrôle graphique (Computer Use) du système d'exploitation. Tous les outils fonctionnent via un unique canal de communication standard d'entrée/sortie (stdio) JSON-RPC 2.0.

| Nom de l'Outil | Domaine | Description | État |
| :--- | :--- | :--- | :--- |
| `execute_action_batch` | <img src="https://img.shields.io/badge/Core%20REPL-10B981?style=flat-square" alt="Core REPL" /> | Exécute des scripts Python/Bash locaux avec `mcp_core` préchargé (modèle Open Interpreter), groupant plusieurs actions sans RTT. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `process_run` | <img src="https://img.shields.io/badge/Syst%C3%A8me%20PTY-10B981?style=flat-square" alt="Système PTY" /> | Lance des commandes shell interactives via PTY pour injecter les mots de passe et franchir les invites Polkit/sudo. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `process_list` | <img src="https://img.shields.io/badge/Syst%C3%A8me%20PTY-10B981?style=flat-square" alt="Système PTY" /> | Interroge le système `/proc` en lecture seule pour sonder les processus actifs sans modifier l'état du système. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `activate_window` | <img src="https://img.shields.io/badge/Syst%C3%A8me%20PTY-10B981?style=flat-square" alt="Système PTY" /> | Bascule le focus au niveau du compositeur d'affichage par Window ID, résolvant les cas de fenêtres multiples par PID. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `get_app_state` | <img src="https://img.shields.io/badge/Palier%20L3-10B981?style=flat-square" alt="Palier L3" /> | Inspecte l'arbre d'accessibilité AT-SPI2 via le médiateur natif Rust (`gui-agent-atspi`) directement en RAM. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `perform_action` | <img src="https://img.shields.io/badge/Palier%20L3-10B981?style=flat-square" alt="Palier L3" /> | Déclenche des actions sémantiques directement en RAM via D-Bus en moins de 50 ms sans déplacer le curseur. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `set_value` | <img src="https://img.shields.io/badge/Palier%20L3-10B981?style=flat-square" alt="Palier L3" /> | Écrit des valeurs textuelles ou numériques directement en mémoire de composant sans frappe clavier physique. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `find_text` | <img src="https://img.shields.io/badge/Palier%20L2-34D399?style=flat-square" alt="Palier L2" /> | Localise les coordonnées de texte à l'écran par OCR local (RapidOCR/Tesseract) sans transmettre d'image. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `screen_capture` | <img src="https://img.shields.io/badge/Palier%20L1-34D399?style=flat-square" alt="Palier L1" /> | Capture le framebuffer brut avec grille cartésienne calibrée pour surfaces opaques (WebGL/Canvas). | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `mouse_click_at` | <img src="https://img.shields.io/badge/Palier%20L1-34D399?style=flat-square" alt="Palier L1" /> | Injecte des clics matériels (`left`, `right`, `middle`, double) aux coordonnées `(x, y)` cibles via pilote natif. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `mouse_drag_smooth` | <img src="https://img.shields.io/badge/Palier%20L1-34D399?style=flat-square" alt="Palier L1" /> | Exécute des trajectoires cinématiques continues interpolées franchissant les seuils d'arrachement de glisser. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `mouse_scroll` | <img src="https://img.shields.io/badge/Palier%20L1-34D399?style=flat-square" alt="Palier L1" /> | Déclenche des défilements molette matériels directionnels pour matérialiser les composants virtualisés. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `key_tap` | <img src="https://img.shields.io/badge/Palier%20L1-34D399?style=flat-square" alt="Palier L1" /> | Injecte des frappes, raccourcis et combinaisons de touches universelles (`Ctrl+L`, `Super+D`, `Return`). | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
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
2. **Pilier 2 : Architecture d'Exécution Haute Efficacité** : Afin d'éliminer la latence réseau des allers-retours (RTT) successifs, l'architecture conçoit un environnement d'exécution local isolé (`execute_action_batch` via `core/repl.py`). Les modèles y projetteront directement leur logique d'inspection et d'action sous forme de code Python exécuté en mémoire hôte via le SDK unifié `mcp_core`. Les vérifications conditionnelles, calculs cinématiques de glisser et scrutations dynamiques se résoudront en un unique aller-retour cognitif à moins de 5 ms avec moins de 15 Mo de RAM (planifié dans la feuille de route Phase 2).
3. **Acquisition d'Écran Ultra-Rapide & Incrustation de Grille Cartésienne** : Lorsqu'un agent demande l'état visuel via `screen_capture` (ou l'alias `gui_take_screenshot`), le serveur capture le framebuffer brut via MSS avec bascule automatique sur KDE Spectacle ou Scrot sous XWayland. Le moteur superpose une grille cartésienne millimétrique à contraste adaptatif à intervalles configurables (ex. 100px), permettant aux modèles de déduire les coordonnées cibles avec certitude mathématique.
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
curl -fsSL https://raw.githubusercontent.com/leandre755/gui_agent/7a49514/linux/install.sh | bash

# Ou exécuter localement depuis un dépôt cloné
./linux/install.sh
```

#### Microsoft Windows (PowerShell)
Lancez PowerShell (utilisateur standard ou administrateur) et exécutez le script d'installation automatisé :

```powershell
# Téléchargement et exécution du script d'installation
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/leandre755/gui_agent/7a49514/windows/install.ps1" -OutFile "install.ps1"
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

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Hammer%20and%20Wrench.png" alt="Tools" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Référence des Outils & CLI

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Gear.png" alt="REPL" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Moteur REPL & Exécution Locale (1 outil)</b></summary>

#### `execute_action_batch`
Exécute des blocs d'actions Python ou Bash directement en mémoire hôte avec le SDK `mcp_core` préchargé (paradigme Open Interpreter), éliminant la latence RTT.
- **Paramètres**:
  - `language` (`str`, par défaut `"python"`): Environnement d'exécution cible (`"python"` ou `"bash"`).
  - `code` (`str`): Script séquentiel contenant logique conditionnelle, boucles et scrutations rapides.
  - `timeout` (`float`, par défaut `30.0`): Délai limite d'exécution en secondes avant interruption du sous-processus.
- **Retourne**: `dict` contenant le statut `status`, les sorties `stdout`, `stderr`, et le temps `elapsed_seconds`.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Window.png" alt="Window" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Contrôles Système & Shell PTY (3 outils)</b></summary>

#### `process_run`
Exécute des commandes shell dans une session pseudo-terminal (PTY) permettant l'injection sécurisée de mots de passe.
- **Paramètres**:
  - `command` (`str` | `list[str]`): Ligne de commande shell ou liste d'arguments à exécuter.
  - `background` (`bool`, par défaut `False`): Lance en arrière-plan détaché (`True`) ou attend la fin (`False`).
  - `sudo_password` (`str | None`, par défaut `None`): Mot de passe injecté sur `stdin` pour élévation Polkit/sudo.
- **Retourne**: `dict` contenant le statut `status`, le code de sortie `returncode`, `stdout` et `stderr`.

#### `process_list`
Sonde la table `/proc` en lecture seule pour inspecter les processus système actifs sans altérer le système.
- **Paramètres**: Aucun.
- **Retourne**: `list[dict]` listant les entrées de processus système actifs avec `pid`, `name` et métadonnées.

#### `activate_window`
Bascule le focus au niveau du compositeur d'affichage en utilisant le Window ID unique, évitant les conflits de PID.
- **Paramètres**:
  - `window_id` (`str` | `int`): Identifiant de fenêtre (Window ID) à placer au premier plan.
- **Retourne**: `dict` confirmant le statut `status` de l'opération et l'identifiant de la fenêtre activée.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Package.png" alt="L3" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Palier L3 — Sémantique RAM & AT-SPI2 (3 outils)</b></summary>

#### `get_app_state`
Inspecte l'arbre d'accessibilité via le médiateur Rust (`gui-agent-atspi`) directement en RAM sans jeton d'image.
- **Paramètres**:
  - `include_screenshot` (`bool`, par défaut `False`): Joint une capture visuelle matricielle optionnelle.
- **Retourne**: `dict` contenant l'arbre structuré, index `element_index`, bornes, états et `snapshot_id`.

#### `perform_action`
Invoque une action sémantique directement en mémoire via D-Bus en moins de 50 ms sans déplacer le curseur.
- **Paramètres**:
  - `element_id` (`str` | `int`): Identifiant de nœud ou index de cache issu du `snapshot_id` actif.
  - `action` (`str`, par défaut `"activate"`): Nom de l'action sémantique (`"activate"`, `"click"`, `"press"`).
- **Retourne**: `dict` confirmant le statut `status` d'exécution, l'identifiant et la réponse de l'action.

#### `set_value`
Écrit des valeurs textuelles ou numériques directement en mémoire de composant sans frappe clavier physique.
- **Paramètres**:
  - `element_id` (`str` | `int`): Identifiant du champ éditable ou composant cible.
  - `value` (`str`): Valeur textuelle ou numérique à assigner directement dans la variable mémoire.
- **Retourne**: `dict` confirmant le statut `status` de mutation, l'identifiant et la valeur enregistrée.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Magnifying%20Glass%20Tilted%20Left.png" alt="Search" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Palier L2 — Vision Locale & OCR (1 outil)</b></summary>

#### `find_text`
Localise les coordonnées de texte à l'écran via les moteurs OCR locaux (RapidOCR / Tesseract) sans latence modèle.
- **Paramètres**:
  - `text` (`str`): Chaîne de texte cible à détecter sur la surface d'affichage.
  - `confidence` (`float`, par défaut `0.85`): Seuil minimal de confiance de reconnaissance (0.0 à 1.0).
- **Retourne**: `dict` contenant le centre de gravité `{"x": int, "y": int}`, cadre englobant et `confidence`.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Computer%20Mouse.png" alt="Mouse" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Palier L1 — Matériel & Émulation d'Entrées (5 outils)</b></summary>

#### `screen_capture`
Capture le framebuffer brut de l'écran avec incrustation d'une grille cartésienne calibrée adaptative.
- **Paramètres**:
  - `show_grid` (`bool`, par défaut `True`): Superpose une grille cartésienne avec labels à contraste adaptatif.
  - `grid_step` (`int`, par défaut `100`): Intervalle en pixels entre les lignes de grille (minimum 20px).
  - `output_path` (`str | None`, par défaut `None`): Chemin de destination avec réservation atomique sécurisée.
- **Retourne**: `dict` contenant le chemin `screenshot_path`, dimensions, format et confirmation de grille.

#### `mouse_click_at`
Injecte des événements de clic matériel via le sous-système d'entrée bas niveau aux coordonnées exactes.
- **Paramètres**:
  - `x` (`int` | `float`): Coordonnée horizontale X absolue en pixels.
  - `y` (`int` | `float`): Coordonnée verticale Y absolue en pixels.
  - `button` (`str`, par défaut `"left"`): Bouton de souris (`"left"`, `"right"`, `"middle"`).
  - `double` (`bool`, par défaut `False`): Émet une séquence de double-clic si activé.
- **Retourne**: `dict` confirmant le statut du clic, les coordonnées cibles et le bouton activé.

#### `mouse_drag_smooth`
Exécute une trajectoire cinématique continue interpolée pour franchir les seuils d'arrachement d'interface.
- **Paramètres**:
  - `from_x` (`int` | `float`): Coordonnée X de départ.
  - `from_y` (`int` | `float`): Coordonnée Y de départ.
  - `to_x` (`int` | `float`): Coordonnée X d'arrivée.
  - `to_y` (`int` | `float`): Coordonnée Y d'arrivée.
  - `duration` (`float`, par défaut `0.5`): Durée totale de l'interpolation cinématique en secondes.
- **Retourne**: `dict` confirmant l'exécution du glisser continu le long de la trajectoire spatiale.

#### `mouse_scroll`
Simule des défilements molette matériels pour matérialiser les composants d'interfaces virtualisées.
- **Paramètres**:
  - `x` (`int` | `float`): Coordonnée X cible où injecter le défilement.
  - `y` (`int` | `float`): Coordonnée Y cible où injecter le défilement.
  - `direction` (`str`, par défaut `"down"`): Direction de défilement (`"up"`, `"down"`, `"left"`, `"right"`).
  - `amount` (`int`, par défaut `5`): Nombre de crans de défilement à injecter.
- **Retourne**: `dict` confirmant l'action de défilement, les coordonnées cibles et le nombre de pas.

#### `key_tap`
Injecte des frappes matérielles, raccourcis système et combinaisons de touches directement vers la fenêtre active.
- **Paramètres**:
  - `key` (`str`): Identifiant de touche (ex. `"Return"`, `"Escape"`, `"Tab"`, `"space"`).
  - `modifiers` (`list[str] | str | None`, par défaut `None`): Modificateurs (ex. `["ctrl"]`, `["alt"]`, `"super"`).
- **Retourne**: `dict` confirmant l'injection de la frappe et la combinaison de modificateurs transmise.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Movie%20Camera.png" alt="Camera" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Enregistrement Vidéo Continu & Audit (2 outils)</b></summary>

#### `gui_start_video_recording`
Démarre un enregistrement vidéo d'écran asynchrone via FFmpeg à faible surcharge pour l'audit comportemental.
- **Paramètres**:
  - `output_path` (`str | None`, par défaut `None`): Chemin du fichier MP4 (par défaut dossier de cache dynamique).
  - `fps` (`int`, par défaut `5`): Fréquence de capture vidéo (1 à 30 FPS).
  - `monitor_index` (`int`, par défaut `1`): Index du moniteur à capturer.
  - `duration` (`int | None`, par défaut `None`): Durée limite optionnelle de l'enregistrement en secondes.
- **Retourne**: `dict` confirmant le démarrage du processus en arrière-plan, le PID et le fichier de sortie.

#### `gui_stop_video_recording`
Arrête proprement l'enregistrement FFmpeg actif, vide le conteneur MP4 et évite les fuites de descripteurs.
- **Paramètres**: Aucun.
- **Retourne**: `dict` contenant le chemin vidéo `output_path`, la confirmation `file_exists` et `file_size_bytes`.

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
curl -fsSLO https://raw.githubusercontent.com/leandre755/gui_agent/7a49514/linux/uninstall.sh
chmod +x uninstall.sh && ./uninstall.sh --purge-data --yes

# Ou désinstallation locale avec purge complète des données et caches
./linux/uninstall.sh --purge-data --yes
```

### 2. Microsoft Windows (PowerShell)

```powershell
# Téléchargement et exécution du désinstallateur automatisé
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/leandre755/gui_agent/7a49514/windows/uninstall.ps1" -OutFile "uninstall.ps1"
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
