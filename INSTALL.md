# Guide d'Installation et Configuration de GUI Agent (`gui-agent`)

Ce guide détaille l'installation, la configuration et le dépannage du serveur FastMCP **GUI Agent** sur **Windows 10/11** et **Linux / macOS**, de manière 100% autonome et sans conflit d'environnement.

---

## 🪟 Installation sous Microsoft Windows

### 1. Méthode 1 : Installation Automatisée en une seule commande (Recommandé)

Ouvrez une invite de commande **PowerShell** (en utilisateur standard ou administrateur) et lancez :

```powershell
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/leandre755/gui_agent/main/install.ps1 | iex"
```

Ou en local depuis le dépôt cloné :

```powershell
.\install.ps1 -Local
```

#### Ce que prend en charge automatiquement le script `install.ps1` :
1. **Utilitaires système (Winget)** : Détection et installation automatique de **FFmpeg** (`Gyan.FFmpeg`) et **Tesseract OCR** (`UB-Mannheim.TesseractOCR`).
2. **Gestionnaire Astral `uv`** : Téléchargement et installation instantanée dans `%USERPROFILE%\.local\bin`.
3. **Déploiement Isolé** : Exécution de `uv tool install gui-agent` avec exposition des binaires `gui-agent.exe` et `mcp-gui-server.exe`.
4. **Configuration MCP Automatique** : Enregistrement automatique dans Claude Code CLI et dans la configuration Antigravity (`%USERPROFILE%\.gemini\config\mcp_config.json`).

---

### 2. Méthode 2 : Installation Manuelle Pas à Pas sous Windows

#### Étape 2.1 — Installer les prérequis système via Winget
```powershell
# 1. FFmpeg (Enregistrement vidéo de l'écran)
winget install --id Gyan.FFmpeg -e --silent --accept-source-agreements --accept-package-agreements

# 2. Tesseract OCR (Reconnaissance et clic de texte)
winget install --id UB-Mannheim.TesseractOCR -e --silent --accept-source-agreements --accept-package-agreements
```

#### Étape 2.2 — Installer Astral UV
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
```

#### Étape 2.3 — Installer `gui-agent` dans son environnement isolé
```powershell
# Depuis PyPI
uv tool install gui-agent --force

# Ou directement depuis le dépôt GitHub
uv tool install "git+https://github.com/leandre755/gui_agent.git" --force
```

#### Étape 2.4 — Vérifier l'installation
```powershell
uv tool list
Get-Command gui-agent
```

---

### 3. Configuration des Clients MCP sous Windows

#### Option A : Claude Code CLI
```powershell
claude mcp add gui-agent -- gui-agent
```

#### Option B : Antigravity CLI (`%USERPROFILE%\.gemini\config\mcp_config.json`)
Ajoutez ou fusionnez dans le fichier `$env:USERPROFILE\.gemini\config\mcp_config.json` :

```json
{
  "mcpServers": {
    "gui-agent": {
      "command": "gui-agent",
      "args": []
    }
  }
}
```

#### Option C : Cursor / VSCode (`%USERPROFILE%\.cursor\mcp.json` ou `cline_mcp_settings.json`)
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

### 4. Dépannage des Erreurs Fréquentes sous Windows

| Problème rencontré | Cause | Solution |
| :--- | :--- | :--- |
| `'gui-agent' n'est pas reconnu en tant que commande` | `%USERPROFILE%\.local\bin` n'est pas encore présent dans la variable `PATH` de la session. | Exécutez : `[System.Environment]::SetEnvironmentVariable('Path', $env:Path + ";$env:USERPROFILE\.local\bin", [System.EnvironmentVariableTarget]::User)` puis redémarrez votre terminal PowerShell. |
| `L'exécution de scripts est désactivée sur ce système` | La stratégie de sécurité PowerShell (`ExecutionPolicy`) est sur `Restricted`. | Utilisez le paramètre `-ExecutionPolicy Bypass` ou configurez : `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. |
| `TesseractNotFoundError` lors de l'OCR | Le binaire Tesseract n'a pas été trouvé dans le PATH. | Installez Tesseract via Winget ou ajoutez `C:\Program Files\Tesseract-OCR` dans votre PATH système. |
| `FFmpeg not found` lors de la capture vidéo | FFmpeg n'est pas dans le PATH après l'installation Winget. | Redémarrez le terminal PowerShell pour recharger les variables d'environnement. |

---

### 5. Désinstallation Propre sous Windows

Pour désinstaller complètement le serveur et nettoyer les configurations MCP :

```powershell
# Désinstallation automatique
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/leandre755/gui_agent/main/uninstall.ps1 | iex"

# Ou avec purge complète des captures d'écran :
.\uninstall.ps1 -PurgeData -Yes
```

---

## 🐧 Installation sous Linux & macOS

### Installation en une seule ligne :
```bash
curl -fsSL https://raw.githubusercontent.com/leandre755/gui_agent/main/install.sh | bash
```

### Désinstallation sous Linux :
```bash
./uninstall.sh --purge-data --yes
```
