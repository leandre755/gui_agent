# Directives de Restructuration & Mises à Jour (MAJ)

Ce document répertorie les exigences architecturales majeures pour la restructuration et l'évolution multi-plateforme du projet `gui_agent`.

---

## 1. Agnosticisme de l'Emplacement & Résolution Dynamique des Chemins

Le code doit être strictement indépendant de son emplacement physique sur le système de fichiers (aucun chemin codé en dur vers un répertoire utilisateur spécifique ou une arborescence locale).

- **Résolution Dynamique des Chemins Système** :
  - Chaque système d'exploitation dispose de sa propre logique de résolution dynamique conforme aux standards natifs.
  - **Linux** : Conformité stricte avec les spécifications XDG Base Directory (`XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME`, `$HOME/.local/share`, `/tmp` ou `XDG_RUNTIME_DIR`).
  - **macOS** : Résolution vers `~/Library/Application Support`, `~/Library/Caches`, et les répertoires standards Apple.
  - **Windows** : Résolution via les variables d'environnement natives (`%APPDATA%`, `%LOCALAPPDATA%`, `%TEMP%`, `ProgramData`).
- **Gestion des Binaires Natifs & Installations** :
  - Résolution dynamique de l'emplacement d'installation du binaire natif (ex. `gui-agent-atspi` ou équivalent plateforme), avec découverte dans les répertoires standards du système, les variables d'environnement prioritaires (`GUI_AGENT_*_BIN`), ou le chemin local de l'environnement virtuel.
- **Gestion des Caches & Artefacts Temporaires** :
  - Les répertoires de stockage des caches (captures d'écran, logs d'exécution, enregistrements vidéo) sont résolus dynamiquement dans le dossier de cache standard de l'OS hôte avec création automatique et sécurisée.

---

## 2. Restructuration Complète de l'Arborescence par Plateforme

Le projet adopte une séparation nette par système d'exploitation afin d'éviter le couplage entre couches spécifiques :

- **Répertoires dédiés et étanches** :
  - `linux/` : Code spécifique Linux (AT-SPI / D-Bus, X11/XWayland, portail XDG RemoteDesktop, uinput/evdev), outils dédiés et scripts d'installation/désinstallation (`install.sh`, `uninstall.sh`).
  - `macos/` : Code spécifique macOS (NSAccessibility, CoreGraphics / Quartz Event Taps, permissions accessibilité), outils dédiés et scripts d'installation/désinstallation (`install.sh`, `uninstall.sh`).
  - `windows/` : Code spécifique Windows (UI Automation, Win32 API, SendInput), outils dédiés et scripts d'installation/désinstallation (`install.ps1`, `uninstall.ps1`).
- **Scripts d'Installation Séparés** :
  - Chaque répertoire de plateforme possède son propre script d'installation automatisé assurant la vérification des prérequis, la compilation éventuelle des binaires natifs et la configuration des dépendances système nécessaires.

---

## 3. Règle Formelle sur l'Outil de Capture Vidéo

- **Conservation Impérative de la Capture Vidéo** :
  - Malgré toute mention ou proposition d'élagage précédente, les outils d'enregistrement vidéo (`gui_start_video_recording`, `gui_stop_video_recording`) **ne doivent en aucun cas être supprimés**.
  - L'outil de capture vidéo fait partie intégrante du périmètre fonctionnel supporté de `gui_agent`.
  - La gestion de ses fichiers de sortie, tampons temporaires et répertoires de stockage s'appuie sur la résolution dynamique des chemins système propres à chaque OS via `VIDEOS_DIR` et `get_videos_dir()`.

---

## 4. État d'Implémentation & Architecture Technique

### 4.1. Structure Épurée à la Racine & Absence de Nesting Redondant
- **Arborescence Racine** :
  - Seuls les trois répertoires de plateformes (`linux/`, `windows/`, `macos/`) subsistent à la racine, accompagnés des métadonnées de projet standard (`README.md`, `pyproject.toml`, `ci.sh`, `Cargo.toml`, etc.).
  - **Déplacement des tests et exemples** : `tests/` et `examples/` ont été déplacés dans `linux/tests/` et `linux/examples/`. Aucun dossier de test ou d'exemple ne subsiste à la racine hors des dossiers d'OS.
  - **Suppression définitive des caches de la racine et de `linux/`** : Le répertoire `screenshots/` ainsi que tout cache résiduel (anciens `target/` de crate de 1,5 Go, `__pycache__`) ont été purgés. Les captures et vidéos sont dirigées dynamiquement vers `$XDG_CACHE_HOME/gui-agent/`.
  - **Aucun doublon ni symlink** : Pas de doublon `win/`, aucun symlink artificiel `gui_agent -> ...`, et aucun répertoire `gui_agent/` laissé à la racine.
  - **Pas de sous-dossier imbriqué `linux/gui_agent/`** : Tout le code Linux réside directement à la racine de `linux/`.
  - **Fichier `.gitignore` exhaustif et durci** : Couvre l'ensemble des environnements virtuels (`venv/`, `.venv/`), des caches d'outils et de linters (`__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`), des médias locaux (`screenshots/`, `videos/`, `*.mp4`, `.cache/`), des artefacts de build (`build/`, `dist/`, `target/`, `**/target/`) et des exécutables natifs multi-plateformes (`bin/`, `**/bin/`, `*.exe`, `*.dll`, `*.so`, `*.dylib`).

### 4.2. Arborescences Dédiées par OS
- `linux/` :
  - `core/` : REPL, PTY, SDK `mcp_core`.
  - `layers/` : Accessibilité AT-SPI / D-Bus, émulation d'entrées, perception visuelle, fenêtrage.
  - `utils/` : Coordonnées, mimétisme cinématique, validation vidéo.
  - `crates/atspi_mediator` : Moteur natif Rust AT-SPI2 / D-Bus.
  - `tests/` : Suite complète de tests unitaires et d'intégration Linux.
  - `examples/` : Exemples d'usage et scripts de validation end-to-end.
  - `paths.py` : Résolution dynamique des chemins Linux XDG.
  - `server.py` : Serveur FastMCP monolithique.
  - `mcp_gui_server.py` : Point d'entrée rétrocompatible.
  - `install.sh` / `uninstall.sh` : Scripts d'automatisation dédiés Linux.
- `macos/` :
  - `.gitkeep` (réservé pour Phase 5 #135).
- `windows/` :
  - `.gitkeep`, `install.ps1`, `uninstall.ps1` (réservé pour Phase 5 #134).

### 4.3. Décision d'Architecture : Bundle Unique Natif par OS (Rust + REPL PyO3)
- **Objectif cible** : Fournir un binaire unique et directement exécutable par système d'exploitation (`gui-agent` pour Linux, `gui-agent.exe` pour Windows, `gui-agent` pour macOS).
- **Compilation sur machine hôte** : Compilation locale unifiée via Cargo (`cargo build --release`) sans dépendance à un environnement virtuel Python complexe à l'exécution.
- **Intégration du REPL CodeAct** : Intégration de l'interpréteur via PyO3 pour l'outil `execute_script`, assurant une exécution locale ultra-rapide (<5ms) et une consommation mémoire minimale (<15 Mo).

### 4.4. Intégration dans le Serveur FastMCP (`linux/server.py`)
- Remplacement du chemin codé en dur `SCREENSHOTS_DIR` par la résolution dynamique `get_screenshots_dir()`.
- Introduction de `VIDEOS_DIR` via `get_videos_dir()` pour le stockage isolé et sécurisé des enregistrements vidéo.
- Conservation intégrale des outils `gui_start_video_recording` et `gui_stop_video_recording`.

### 4.5. Protocole de Publication et Revue
- Les Pull Requests sont publiées sous le compte GitHub **personal agent**.
- La temporisation pour l'attente du verdict Greptile distant est fixée à **5 minutes minimum (300 secondes)** (ne pas configurer de timer court à 30 secondes).
