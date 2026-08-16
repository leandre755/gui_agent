<p align="center">
  <img src="https://files.catbox.moe/udf9j4.jpeg" alt="gui-agent Hero Banner" width="100%" style="border-radius: 8px;" />
</p>

<h1 align="center"><img src="https://files.catbox.moe/xei715.png" alt="gui-agent Logo" width="114" style="vertical-align: middle; margin-right: 12px;" /> gui-agent</h1>

<p align="center"><b>Serveur FastMCP Monolithique pour le Contrôle Graphique (Computer Use) sous Linux et Windows</b></p>

<p align="center">🌐 <b><a href="README.md">English</a></b> | <b><a href="README.fr.md">Français</a></b></p>

<p align="center">
  <a href="#-fonctionnalités-principales"><img src="https://img.shields.io/badge/Fonctionnalit%C3%A9s-→-10B981?style=flat-square" alt="Fonctionnalités" /></a>
  <a href="#-architecture--flux-de-fonctionnement"><img src="https://img.shields.io/badge/Architecture-→-10B981?style=flat-square" alt="Architecture" /></a>
  <a href="#-installation"><img src="https://img.shields.io/badge/Installation-→-10B981?style=flat-square" alt="Installation" /></a>
  <a href="#-configuration-des-clients-mcp"><img src="https://img.shields.io/badge/Clients_MCP-→-10B981?style=flat-square" alt="Clients MCP" /></a>
  <a href="#-référence-du-toolset--cli"><img src="https://img.shields.io/badge/Toolset-→-10B981?style=flat-square" alt="Toolset" /></a>
  <a href="#-désinstallation-propre"><img src="https://img.shields.io/badge/D%C3%A9sinstallation-→-10B981?style=flat-square" alt="Désinstallation" /></a>
  <a href="#-développement--qualité-zero-slop"><img src="https://img.shields.io/badge/D%C3%A9veloppement-→-10B981?style=flat-square" alt="Développement" /></a>
</p>

<p align="center">
  <a href="https://github.com/leandre755/gui_agent/releases/tag/v0.1.0"><img src="https://img.shields.io/badge/version-0.1.0-3FB950?style=flat-square" alt="Version 0.1.0" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-34D399?style=flat-square" alt="Python 3.10+" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/licence-MIT-F0883E?style=flat-square" alt="Licence MIT" /></a>
  <a href="#"><img src="https://img.shields.io/badge/plateforme-Linux%20%7C%20Windows-10B981?style=flat-square" alt="Plateforme Linux | Windows" /></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/Protocole_MCP-1.2.0+-10B981?style=flat-square" alt="Protocole MCP 1.2.0+" /></a>
</p>

### Pourquoi gui-agent ?

L'automatisation d'interfaces graphiques pour agents IA repose souvent sur une mosaïque d'outils séparés pour la capture d'écran, l'émulation des entrées, la gestion des fenêtres et l'OCR. Multiplier ces processus augmente la latence, consomme plusieurs centaines de mégaoctets de RAM et échoue dès qu'une fenêtre change d'état.

**gui-agent** regroupe ces fonctions dans un serveur FastMCP unique communiquant via stdio. Il fournit 21 outils pour Linux (X11/XWayland) et Windows dans un seul processus utilisant moins de 50 Mo de RAM, sans nécessiter de runtime de navigateur lourd pour les opérations de bureau (sauf en cas d'appel explicite à `gui_web_action`) ni dépendance à des API de vision cloud.

Le serveur capture directement le framebuffer, superpose une grille de repérage cartésienne pour fiabiliser le ciblage spatial des modèles de vision, et transmet les entrées utilisateur via les appels système et utilitaires natifs (`xdotool`, API Win32). La détection d'éléments s'appuie sur la recherche de motifs OpenCV et un OCR local avec repli automatique.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Activities/Bullseye.png" alt="Bullseye" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Fonctionnalités Principales

Le serveur expose 21 outils FastMCP pour le contrôle graphique de l'OS. Tous les outils communiquent via un unique canal stdio JSON-RPC 2.0.

| Nom de l'Outil | Domaine | Description | État |
| :--- | :--- | :--- | :--- |
| `gui_get_screen_info` | <img src="https://img.shields.io/badge/%C3%89cran-10B981?style=flat-square" alt="Écran" /> | Renvoie la résolution d'écran, les moniteurs connectés, les coordonnées et l'état failsafe. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_take_screenshot` | <img src="https://img.shields.io/badge/%C3%89cran-10B981?style=flat-square" alt="Écran" /> | Capture l'écran complet ou une zone avec incrustation optionnelle de grille cartésienne. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_mouse_move` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Déplace le curseur vers des coordonnées absolues `(x, y)` ou normalisées `[0, 1000]`. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_mouse_click` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Envoie des clics simples, doubles ou triples (`left`, `right`, `middle`) aux coordonnées cibles. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_mouse_drag` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Effectue un glisser-déposer de `(x1, y1)` vers `(x2, y2)` avec durée paramétrable. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_mouse_scroll` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Fait défiler la molette selon l'axe horizontal ou vertical (`up`, `down`, `left`, `right`). | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_keyboard_type` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Saisit une chaîne de texte avec délai paramétrable entre chaque caractère. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_keyboard_press` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Envoie des touches spéciales et combinaisons de raccourcis (`ctrl+c`, `super`, `alt+tab`, `Return`). | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_clipboard_get` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Lit le presse-papiers avec repli automatique multi-backend (`pyperclip`, `xclip`, `xsel`). | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_clipboard_set` | <img src="https://img.shields.io/badge/Entr%C3%A9e-10B981?style=flat-square" alt="Entrée" /> | Écrit du texte dans le presse-papiers du système via les backends disponibles. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_window_list` | <img src="https://img.shields.io/badge/Fen%C3%AAtre-10B981?style=flat-square" alt="Fenêtre" /> | Liste les fenêtres ouvertes avec leurs identifiants, PID, titres et classes WM. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_window_focus` | <img src="https://img.shields.io/badge/Fen%C3%AAtre-10B981?style=flat-square" alt="Fenêtre" /> | Active et place une fenêtre cible au premier plan par son identifiant. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_window_resize_move` | <img src="https://img.shields.io/badge/Fen%C3%AAtre-10B981?style=flat-square" alt="Fenêtre" /> | Déplace et redimensionne une fenêtre selon les coordonnées et dimensions spécifiées. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_window_close` | <img src="https://img.shields.io/badge/Fen%C3%AAtre-10B981?style=flat-square" alt="Fenêtre" /> | Ferme une fenêtre d'application via les protocoles standard du gestionnaire de fenêtres. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_app_launch` | <img src="https://img.shields.io/badge/Fen%C3%AAtre-10B981?style=flat-square" alt="Fenêtre" /> | Lance un exécutable en tâche de fond asynchrone ou en exécution synchrone. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_find_template` | <img src="https://img.shields.io/badge/Vision-34D399?style=flat-square" alt="Vision" /> | Localise une image modèle sur l'écran par comparaison de motifs OpenCV. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_find_text` | <img src="https://img.shields.io/badge/Vision-34D399?style=flat-square" alt="Vision" /> | Localise les coordonnées d'un texte à l'écran via OCR (Tesseract / RapidOCR). | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_click_text` | <img src="https://img.shields.io/badge/Vision-34D399?style=flat-square" alt="Vision" /> | Recherche un texte à l'écran par OCR et clique directement en son centre. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_web_action` | <img src="https://img.shields.io/badge/Web-34D399?style=flat-square" alt="Web" /> | Exécute des actions de navigateur Playwright (`aria_tree`, `click`, `type`, `screenshot`). | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_start_video_recording` | <img src="https://img.shields.io/badge/M%C3%A9dia-F0883E?style=flat-square" alt="Média" /> | Démarre un enregistrement vidéo de l'écran en tâche de fond via FFmpeg (`x11grab` / H.264). | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |
| `gui_stop_video_recording` | <img src="https://img.shields.io/badge/M%C3%A9dia-F0883E?style=flat-square" alt="Média" /> | Arrête l'enregistrement FFmpeg en cours et finalise le conteneur MP4. | <img src="https://img.shields.io/badge/Actif-3FB950?style=flat-square" alt="Actif" /> |

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Gear.png" alt="Gear" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Architecture & Flux de Fonctionnement

**gui-agent** relie les clients MCP (Claude Code, Antigravity CLI, Cursor) à l'environnement de bureau. Il exécute les entrées utilisateur, capture les tampons d'affichage et interroge les fenêtres via les interfaces système locales.

<p align="center">
  <img src="https://gist.githubusercontent.com/lender926-lab/050b95747c45950573c28906fcb1fae6/raw/exc-how-it-works-fr.svg" alt="Architecture & Flux gui-agent" width="100%" style="border-radius: 10px;" />
</p>

### Pipeline d'Exécution Technique

1. **Capture d'Écran & Grille de Coordonnées** : Lors d'un appel à `gui_take_screenshot`, le serveur capture le framebuffer via MSS, avec repli automatique vers Spectacle ou Scrot sous XWayland. Il superpose une grille de repérage configurable (100 px par défaut) avec des libellés à fort contraste pour faciliter la lecture des coordonnées par les modèles de vision.
2. **Interface stdio FastMCP** : Le serveur communique via stdio en JSON-RPC 2.0. Les paramètres des outils sont validés à l'exécution par des modèles Pydantic, sans port réseau ouvert ni démon persistant.
3. **Normalisation des Coordonnées** : Les outils acceptent des coordonnées absolues en pixels `(x, y)` ou coordonnées normalisées `[0, 1000]`. Le convertisseur applique le bornage aux limites de l'écran et gère les configurations multi-écrans et les facteurs d'échelle DPI.
4. **Gestion des Entrées & Fenêtres Natives** : Les événements souris et clavier sont transmis au serveur d'affichage (`xdotool`/`Xlib` sous Linux, API Win32 sous Windows) avec temporisations configurables. La gestion des fenêtres s'appuie sur `wmctrl` et `xprop`.
5. **Vision Locale, OCR & Playwright** : OpenCV localise les éléments graphiques par comparaison de motifs. La détection de texte utilise Tesseract avec repli RapidOCR ONNX. L'automatisation web s'effectue via Playwright par inspection directe de l'arbre DOM/ARIA.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Package.png" alt="Package" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Installation

> Pour les guides par système, le dépannage et l'installation hors-ligne, consultez [**INSTALL.md**](INSTALL.md).

### 1. Installation Automatisée (Recommandée)

#### Linux (Bash)
Exécutez le script d'installation pour vérifier les dépendances, installer `uv`, créer l'environnement virtuel et enregistrer le serveur MCP :

```bash
# Installateur curl en une ligne
curl -fsSL https://raw.githubusercontent.com/leandre755/gui_agent/main/install.sh | bash

# Ou localement depuis un dépôt cloné
./install.sh
```

#### Microsoft Windows (PowerShell)
Exécutez l'installateur PowerShell (utilisateur standard ou administrateur) :

```powershell
# Installateur PowerShell en une ligne
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/leandre755/gui_agent/main/install.ps1 | iex"

# Ou localement depuis un dépôt cloné
.\install.ps1 -Local
```

### 2. Déploiement Isolé via uv tool

Installez `gui-agent` dans un environnement isolé avec des points d'entrée CLI globaux :

```bash
# Installer depuis PyPI
uv tool install gui-agent

# Ou installer depuis le dépôt GitHub
uv tool install "git+https://github.com/leandre755/gui_agent.git"

# Mettre à niveau vers la dernière version
uv tool upgrade gui-agent
```

### 3. Prérequis Système Linux

Installez les paquets système pour la gestion des fenêtres, la capture, l'OCR et le presse-papiers :

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
Renvoie les dimensions d'écran, les moniteurs connectés, les coordonnées et l'état failsafe.
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
- **Retourne** : `dict` contenant `screenshot_path` (chemin absolu résolu), `raw_screenshot_path`, `resolution`, `grid_applied` et `renamed_due_to_conflict`.

#### `gui_mouse_move`
Déplace le curseur de la souris vers les coordonnées cibles.
- **Paramètres** :
  - `x` (`float`) : Position X cible.
  - `y` (`float`) : Position Y cible.
  - `duration` (`float`, valeur par défaut `0.2`) : Durée d'interpolation du mouvement en secondes.
  - `normalized` (`bool`, valeur par défaut `False`) : Définir à `True` lors de l'utilisation de coordonnées `[0, 1000]`.
  - `monitor_index` (`int`, valeur par défaut `1`) : Moniteur de référence pour les calculs de coordonnées.

#### `gui_mouse_click`
Effectue des clics de souris aux coordonnées cibles.
- **Paramètres** :
  - `x` (`float`) : Position X cible.
  - `y` (`float`) : Position Y cible.
  - `button` (`str`, valeur par défaut `"left"`) : Bouton de souris (`"left"`, `"right"`, `"middle"`).
  - `clicks` (`int`, valeur par défaut `1`) : Nombre de clics à exécuter.
  - `normalized` (`bool`, valeur par défaut `False`) : Définir à `True` pour les coordonnées `[0, 1000]`.
  - `monitor_index` (`int`, valeur par défaut `1`) : Moniteur de référence.

#### `gui_mouse_drag`
Effectue un glisser-déposer à la souris entre deux positions.
- **Paramètres** :
  - `x1` (`float`) : Position X de départ.
  - `y1` (`float`) : Position Y de départ.
  - `x2` (`float`) : Position X d'arrivée.
  - `y2` (`float`) : Position Y d'arrivée.
  - `duration` (`float`, valeur par défaut `0.5`) : Durée de l'animation de glissement en secondes.
  - `normalized` (`bool`, valeur par défaut `False`) : Définir à `True` pour les coordonnées `[0, 1000]`.
  - `monitor_index` (`int`, valeur par défaut `1`) : Moniteur de référence.

#### `gui_mouse_scroll`
Fait défiler la molette de souris selon l'axe vertical ou horizontal.
- **Paramètres** :
  - `clicks` (`int`) : Nombre de crans de défilement (entier positif).
  - `direction` (`str`, valeur par défaut `"down"`) : Direction (`"up"`, `"down"`, `"left"`, `"right"`).

#### `gui_keyboard_type`
Saisit du texte de manière séquentielle avec un délai paramétrable entre chaque touche.
- **Paramètres** :
  - `text` (`str`) : Contenu textuel à saisir.
  - `delay` (`float`, valeur par défaut `0.06`) : Délai de base entre les frappes de touches en secondes.

#### `gui_keyboard_press`
Envoie des frappes de touches individuelles ou des combinaisons de raccourcis.
- **Paramètres** :
  - `key` (`str`) : Identifiant de touche ou accord (ex. `"Return"`, `"Escape"`, `"ctrl+c"`, `"alt+tab"`, `"super"`).

#### `gui_clipboard_get`
Lit le contenu textuel du presse-papiers système.
- **Paramètres** : Aucun.
- **Retourne** : `dict` contenant le `text` du presse-papiers, la longueur `length` et la méthode `method` d'extraction.

#### `gui_clipboard_set`
Écrit une chaîne de texte dans le presse-papiers du système.
- **Paramètres** :
  - `text` (`str`) : Contenu textuel à stocker dans le presse-papiers.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Window.png" alt="Window" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Contrôle des Fenêtres & Processus (5 outils)</b></summary>

#### `gui_window_list`
Liste les fenêtres ouvertes avec leur identifiant, titre, PID et classe de fenêtre.
- **Paramètres** : Aucun.
- **Retourne** : `dict` avec tableau `windows` contenant l'`id`, `title`, `pid` et `wm_class` de chaque fenêtre.

#### `gui_window_focus`
Place la fenêtre cible au premier plan à partir de son identifiant.
- **Paramètres** :
  - `window_id` (`int`) : Identifiant numérique de fenêtre obtenu via `gui_window_list`.

#### `gui_window_resize_move`
Déplace et redimensionne une fenêtre d'application aux coordonnées et dimensions indiquées.
- **Paramètres** :
  - `window_id` (`int`) : Identifiant numérique de la fenêtre cible.
  - `x` (`int`) : Nouvelle coordonnée X du coin supérieur gauche.
  - `y` (`int`) : Nouvelle coordonnée Y du coin supérieur gauche.
  - `width` (`int`) : Nouvelle largeur de la fenêtre en pixels.
  - `height` (`int`) : Nouvelle hauteur de la fenêtre en pixels.

#### `gui_window_close`
Ferme une fenêtre d'application via les protocoles standard du gestionnaire de fenêtres.
- **Paramètres** :
  - `window_id` (`int`) : Identifiant numérique de la fenêtre cible.

#### `gui_app_launch`
Lance une commande ou un exécutable du système d'exploitation.
- **Paramètres** :
  - `command` (`str`) : Ligne de commande shell ou chemin de l'exécutable à lancer.
  - `background` (`bool`, valeur par défaut `True`) : Exécuter de manière détachée en tâche de fond (`True`) ou synchrone (`False`).

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Magnifying%20Glass%20Tilted%20Left.png" alt="Search" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Vision & Automatisation OCR (3 outils)</b></summary>

#### `gui_find_template`
Localise une image modèle sur l'écran par comparaison de motifs OpenCV.
- **Paramètres** :
  - `template_path` (`str`) : Chemin vers le fichier de l'image modèle de référence.
  - `threshold` (`float`, valeur par défaut `0.8`) : Seuil de confiance (entre 0.01 et 1.0).
  - `monitor_index` (`int`, valeur par défaut `1`) : Index du moniteur à inspecter.
- **Retourne** : `dict` contenant les coordonnées du centre détecté `(x, y)` et le score `confidence`.

#### `gui_find_text`
Localise du texte à l'écran par OCR (Tesseract / RapidOCR) et renvoie les coordonnées du cadre englobant.
- **Paramètres** :
  - `text` (`str`) : Chaîne de caractères cible à découvrir.
  - `confidence` (`float`, valeur par défaut `0.6`) : Score minimal de confiance OCR (0.0 à 1.0).
  - `monitor_index` (`int`, valeur par défaut `1`) : Index du moniteur où effectuer la recherche.
- **Retourne** : `dict` contenant `text_found`, le centroïde `(x, y)`, `confidence` et la boîte englobante `[x, y, w, h]`.

#### `gui_click_text`
Recherche un texte à l'écran par OCR et clique au centre de la zone correspondante.
- **Paramètres** :
  - `text` (`str`) : Chaîne de texte cible à localiser et cliquer.
  - `button` (`str`, valeur par défaut `"left"`) : Bouton de souris à actionner (`"left"`, `"right"`, `"middle"`).
  - `clicks` (`int`, valeur par défaut `1`) : Nombre de clics à effectuer.
  - `monitor_index` (`int`, valeur par défaut `1`) : Moniteur cible.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Movie%20Camera.png" alt="Camera" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Web & Enregistrement Multimédia (3 outils)</b></summary>

#### `gui_web_action`
Automatise des pages web dans Chromium headless via Playwright.
- **Paramètres** :
  - `url` (`str`) : Adresse web ou URL de fichier local vers laquelle naviguer.
  - `action` (`str`, valeur par défaut `"aria_tree"`) : Action à exécuter (`"aria_tree"`, `"click"`, `"type"`, `"screenshot"`).
  - `selector` (`str | None`, valeur par défaut `None`) : Sélecteur CSS ou XPath pour les actions `click` et `type`.
  - `text` (`str | None`, valeur par défaut `None`) : Données textuelles à saisir lorsque `action="type"`.
  - `viewport_width` (`int`, valeur par défaut `1280`) : Largeur de fenêtre du navigateur.
  - `viewport_height` (`int`, valeur par défaut `720`) : Hauteur de fenêtre du navigateur.
  - `timeout_ms` (`int`, valeur par défaut `30000`) : Délai maximal de navigation et de localisation en millisecondes.

#### `gui_start_video_recording`
Démarre un enregistrement vidéo de l'écran en tâche de fond via FFmpeg (`x11grab` / H.264).
- **Paramètres** :
  - `output_path` (`str | None`, valeur par défaut `None`) : Chemin du fichier de destination (défaut : MP4 horodaté dans le dossier des captures).
  - `fps` (`int`, valeur par défaut `5`) : Cadence de capture vidéo (1 à 30 IPS).
  - `monitor_index` (`int`, valeur par défaut `1`) : Index du moniteur cible.
  - `duration` (`int | None`, valeur par défaut `None`) : Limite optionnelle de durée automatique en secondes.

#### `gui_stop_video_recording`
Arrête l'enregistrement FFmpeg en cours et valide le fichier MP4 produit.
- **Paramètres** : Aucun.
- **Retourne** : `dict` contenant `output_path`, `file_exists` et `file_size_bytes`.

</details>

<details>
<summary><b><img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Control%20Knobs.png" alt="Config" width="22" height="22" style="vertical-align: middle; margin-right: 6px;" /> Variables d'Environnement (Configuration)</b></summary>

| Variable | Description | Valeur par Défaut |
| :--- | :--- | :--- |
| `DISPLAY` | Identifiant du serveur d'affichage X11 cible. | `:0` |
| `GUI_AGENT_SCREENSHOTS_DIR` | Répertoire où sont enregistrées les captures, découpes et vidéos d'écran. | `~/.local/share/gui-agent/screenshots` |

</details>

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Wastebasket.png" alt="Trash" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Désinstallation Propre

Pour désinstaller `gui-agent`, supprimer les environnements isolés et nettoyer les configurations MCP enregistrées :

### 1. Linux & macOS (Bash)

```bash
# Désinstallateur distant automatisé
curl -fsSL https://raw.githubusercontent.com/leandre755/gui_agent/main/uninstall.sh | bash

# Désinstallation locale avec purge complète des données et captures
./uninstall.sh --purge-data --yes
```

### 2. Microsoft Windows (PowerShell)

```powershell
# Désinstallateur distant automatisé
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/leandre755/gui_agent/main/uninstall.ps1 | iex"

# Désinstallation locale avec purge complète des données et captures
.\uninstall.ps1 -PurgeData -Yes
```

#### Éléments nettoyés par le désinstallateur :
- Supprime les binaires `gui-agent` et `mcp-gui-server` de `~/.local/bin` (ou `%USERPROFILE%\.local\bin`).
- Désenregistre le serveur MCP de la configuration du CLI Claude Code.
- Nettoie les entrées JSON du fichier `mcp_config.json` d'Antigravity.
- Purge les répertoires temporaires et supprime optionnellement le dossier de captures (`--purge-data` / `-PurgeData`).

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Shield.png" alt="Shield" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Développement & Qualité Zero-Slop

Le projet applique des normes d'ingénierie logicielle strictes, vérifiées par un pipeline de 8 couches de hooks pre-commit et une couverture de tests complète.

### 1. Configuration de l'Environnement Local

```bash
# Cloner le dépôt
git clone https://github.com/leandre755/gui_agent.git
cd gui_agent

# Initialiser l'environnement virtuel avec Astral UV
uv venv
source .venv/bin/activate

# Installer le paquet en mode éditable avec les dépendances de développement
uv pip install -e ".[dev]"
```

### 2. Exécution des Suites de Tests

```bash
# Exécuter les tests unitaires et d'intégration
pytest -v tests/
```

### 3. Vérification Pre-Commit Zero-Slop en 8 Couches

Chaque commit est filtré par 8 couches strictes de validation statique pour éliminer la dette technique et les vulnérabilités de sécurité :

```bash
# Exécuter le hook de validation Zero-Slop en 8 couches localement
ALLOW_CONFIG_EDIT=1 ./.githooks/pre-commit
```

| Couche | Validateur | Périmètre & Invariants de Qualité Appliqués |
| :--- | :--- | :--- |
| 1 | `anti-leak` | Bloque les secrets, clés privées et variables `.env` dans les fichiers indexés. |
| 2 | `pip-audit` | Analyse les dépendances installées contre les bases de vulnérabilités CVE. |
| 3 | `ruff check` | Applique les règles de lint, les standards PEP 8 et la syntaxe Python 3.10+. |
| 4 | `ruff format` | Contrôle le formatage uniforme du code sur l'ensemble des sources Python. |
| 5 | `mypy` | Exécute la vérification statique des types sur toute la base de code. |
| 6 | `sonar/smells` | Contrôle la complexité cognitive (McCabe C90 <= 25), bugs et mauvaises pratiques. |
| 7 | `bandit` | Analyse l'AST pour détecter les failles de sécurité (appels subprocess risqués). |
| 8 | `semgrep` | Scanner SAST identifiant les vulnérabilités de sécurité et motifs dangereux. |

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Scroll.png" alt="Scroll" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Licence

Ce projet est distribué sous les termes de la [Licence MIT](LICENSE).

Copyright (c) 2026 Leandre. Tous droits réservés.
