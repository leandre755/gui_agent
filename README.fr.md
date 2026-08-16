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

### La Philosophie : Pourquoi gui-agent ?

Les agents IA autonomes interagissant avec les interfaces graphiques modernes sont fréquemment entravés par des architectures fragmentées, des micro-serveurs instables et une empreinte mémoire exorbitante. Les dispositifs d'automatisation traditionnels contraignent les modèles à jongler entre des processus hétérogènes pour la capture d'écran, l'émulation des entrées, la gestion des fenêtres et la reconnaissance optique de caractères. Cette dispersion engendre une latence critique, des taux d'échec élevés sur les environnements de bureau dynamiques, et une surconsommation de ressources qui sature rapidement les stations de travail aux capacités limitées.

**gui-agent** résout cette friction architecturale en fournissant un serveur FastMCP unifié et monolithique, spécialement conçu pour un contrôle graphique (Computer Use) direct et à très faible latence sous Linux (X11/XWayland) et Windows. En consolidant vingt-et-un outils haute performance au sein d'une unique liaison stdio résiliente, **gui-agent** maintient une empreinte mémoire minimale inférieure à 50 Mo de RAM, garantissant une exécution fluide sur les processeurs double-cœur et les environnements virtualisés sans nécessiter d'environnement d'exécution de navigateur pour les outils desktop (l'automatisation de navigateur est strictement localisée à `gui_web_action`) ni de dépendances cloud de vision externes.

Sous le capot, **gui-agent** associe une acquisition d'écran à la milliseconde à une grille de coordonnées cartésiennes intelligente, permettant aux grands modèles de langage de localiser précisément les cibles visuelles sans hallucinations spatiales. En combinant des répartiteurs d'entrées natifs de l'OS, l'introspection de la hiérarchie des fenêtres, la correspondance de motifs OpenCV et l'extraction OCR locale avec des mécanismes de repli automatisés, le système garantit une exécution déterministe, une gestion de cycle de vie sans fuite de processus et un contrôle au pixel près à travers les flux de travail bureautiques les plus exigeants.

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

**gui-agent** fonctionne comme une passerelle en boucle fermée pour le Computer Use entre les moteurs de raisonnement LLM de pointe et le système d'exploitation hôte. Le pipeline d'exécution garantit l'absence d'hallucinations spatiales grâce à une normalisation déterministe des coordonnées et des mécanismes de repli hybrides.

<p align="center">
  <img src="https://gist.githubusercontent.com/lender926-lab/050b95747c45950573c28906fcb1fae6/raw/exc-how-it-works-fr.svg" alt="Architecture & Flux gui-agent" width="100%" style="border-radius: 10px;" />
</p>

### Pipeline d'Exécution Technique

1. **Acquisition d'Écran Ultra-Rapide & Incrustation de Grille Cartésienne** : Lorsqu'un agent demande l'état visuel via `gui_take_screenshot`, le serveur capture le framebuffer brut via MSS. Si la composition XWayland produit une image vide, il bascule de manière transparente sur KDE Spectacle ou Scrot. Le moteur superpose une grille cartésienne millimétrique avec des étiquettes à contraste adaptatif à intervalles configurables (ex. 100px), permettant aux LLM de déduire les coordonnées cibles avec certitude mathématique.
2. **Interface stdio JSON-RPC 2.0 Standardisée** : Bâti sur FastMCP, le serveur communique via les flux standards d'entrée/sortie sans ouvrir de ports réseau vulnérables ni déployer de topologies de démons complexes. Toutes les signatures d'outils sont typées statiquement et validées via des schémas Pydantic.
3. **Moteur Double de Normalisation des Coordonnées** : Le serveur accepte les coordonnées en pixels physiques absolus `(x, y)` ou en ratios normalisés `[0, 1000]` sur toute géométrie d'affichage ou configuration multi-écrans. Un convertisseur automatique gère le bornage aux limites, la mise à l'échelle DPI et la translation des coordonnées.
4. **Répartiteur d'Entrées et de Fenêtres OS Natif** : Les frappes, raccourcis, clics de souris et opérations de glisser sont acheminés via des pilotes natifs à faible latence (`xdotool` et `python-xlib` sous Linux, API Win32 sous Windows). Des micro-délais humanisés émulent une interaction utilisateur naturelle. Les commandes de gestion de fenêtres (`wmctrl` / `xprop`) inspectent et manipulent l'état des fenêtres sans verrouiller le gestionnaire de fenêtres.
5. **Vision Locale, OCR & Automatisation Playwright** : La correspondance de motifs (`cv2.matchTemplate`) permet une détection robuste des icônes malgré les variations de thèmes. La détection de texte combine Tesseract OCR avec le repli ONNX RapidOCR. L'automatisation web s'appuie sur Playwright pour inspecter les arbres ARIA et manipuler directement les nœuds DOM sans ambiguïté visuelle.

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Package.png" alt="Package" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Installation

> Pour les instructions détaillées par OS, les matrices de dépannage et les configurations hors-ligne, consultez le [**Guide d'Installation Détaillé (INSTALL.md)**](INSTALL.md).

### 1. Installation Automatisée (Recommandée)

#### Linux (Bash)
Exécutez le script d'installation automatisé pour vérifier les dépendances, installer Astral `uv`, configurer l'environnement isolé et enregistrer le serveur MCP :

```bash
# Installateur curl en une ligne
curl -fsSL https://raw.githubusercontent.com/leandre755/gui_agent/main/install.sh | bash

# Ou localement depuis un dépôt cloné
./install.sh
```

#### Microsoft Windows (PowerShell)
Lancez PowerShell (utilisateur standard ou administrateur) et exécutez :

```powershell
# Installateur PowerShell en une ligne
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/leandre755/gui_agent/main/install.ps1 | iex"

# Ou localement depuis un dépôt cloné
.\install.ps1 -Local
```

### 2. Déploiement Isolé via uv tool

Installez `gui-agent` directement dans un environnement isolé avec des points d'entrée CLI globaux :

```bash
# Installer depuis PyPI
uv tool install gui-agent

# Ou installer depuis le dépôt GitHub
uv tool install "git+https://github.com/leandre755/gui_agent.git"

# Mettre à niveau vers la dernière version
uv tool upgrade gui-agent
```

### 3. Prérequis Système Linux

Sous Linux, installez les bibliothèques natives de gestion de fenêtres, d'OCR et multimédias :

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
- **Retourne** : `dict` contenant `screenshot_path` (chemin absolu résolu), `raw_screenshot_path`, `resolution`, `grid_applied` et `renamed_due_to_conflict`.

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
  - `output_path` (`str | None`, valeur par défaut `None`) : Chemin du fichier de destination (défaut : MP4 horodaté dans le dossier des captures).
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
| `GUI_AGENT_SCREENSHOTS_DIR` | Répertoire où sont enregistrées les captures, découpes et vidéos d'écran. | `~/.local/share/gui-agent/screenshots` |

</details>

---

## <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Wastebasket.png" alt="Trash" width="28" height="28" style="vertical-align: middle; margin-right: 8px;" /> Désinstallation Propre

Pour purger proprement `gui-agent`, supprimer les environnements isolés et retirer les configurations MCP enregistrées :

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
