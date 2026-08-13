# ==============================================================================
# GUI Agent - Automated Windows Installation Script (PowerShell)
# Method: Isolated tool installation via Astral `uv tool install`
# ==============================================================================

[CmdletBinding()]
param(
    [Alias("y", "no-prompt")]
    [switch]$Yes,

    [Alias("d")]
    [switch]$DryRun,

    [Alias("l")]
    [switch]$Local,

    [switch]$SkipMcpConfig
)

$ErrorActionPreference = "Stop"

function Write-Color([string]$text, [string]$color) {
    Write-Host $text -ForegroundColor $color
}

function Log-Info([string]$msg) {
    Write-Color "[INFO] $msg" "Cyan"
}

function Log-Success([string]$msg) {
    Write-Color "[SUCCESS] $msg" "Green"
}

function Log-Warn([string]$msg) {
    Write-Color "[WARN] $msg" "Yellow"
}

function Log-Error([string]$msg) {
    Write-Color "[ERROR] $msg" "Red"
}

function Print-Banner {
    Write-Color "============================================================" "Cyan"
    Write-Color "       GUI Agent - Windows Desktop MCP Server               " "Cyan"
    Write-Color "          Automated Production Installer                    " "Cyan"
    Write-Color "============================================================" "Cyan"
    Write-Host ""
}

Print-Banner

# Step 1: Environment Check
Log-Info "1/5 - Vérification de l'environnement Windows..."
$runningOnWindows = ($env:OS -like "*Windows*" -or ([System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT))
if (-not $runningOnWindows) {
    Log-Error "Ce script d'installation est réservé aux environnements Microsoft Windows 10/11."
    exit 1
}
Log-Success "Système d'exploitation compatible : Windows ($([System.Environment]::OSVersion.VersionString))"

# Step 2: System Tools Check (Winget)
Log-Info "2/5 - Vérification des utilitaires système recommandés (FFmpeg, Tesseract)..."
$hasWinget = (Get-Command winget -ErrorAction SilentlyContinue) -ne $null
$hasFfmpeg = (Get-Command ffmpeg -ErrorAction SilentlyContinue) -ne $null
$hasTesseract = (Get-Command tesseract -ErrorAction SilentlyContinue) -ne $null

$missingTools = @()
if (-not $hasFfmpeg) { $missingTools += "FFmpeg (Gyan.FFmpeg)" }
if (-not $hasTesseract) { $missingTools += "Tesseract OCR (UB-Mannheim.TesseractOCR)" }

if ($missingTools.Count -gt 0) {
    Log-Warn "Outils recommandés non détectés dans le PATH : $($missingTools -join ', ')"
    if ($hasWinget) {
        if ($DryRun) {
            Log-Info "[Dry-Run] winget install --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements"
            Log-Info "[Dry-Run] winget install --id UB-Mannheim.TesseractOCR --accept-source-agreements --accept-package-agreements"
        } elseif ($Yes) {
            Log-Info "Installation automatique des utilitaires recommandés via winget..."
            if (-not $hasFfmpeg) { winget install --id Gyan.FFmpeg -e --silent --accept-source-agreements --accept-package-agreements }
            if (-not $hasTesseract) { winget install --id UB-Mannheim.TesseractOCR -e --silent --accept-source-agreements --accept-package-agreements }
        } else {
            $response = Read-Host "Voulez-vous installer automatiquement FFmpeg et Tesseract via winget ? [O/n]"
            if ($response -match "^(o|oui|y|yes|)$") {
                if (-not $hasFfmpeg) { winget install --id Gyan.FFmpeg -e --silent --accept-source-agreements --accept-package-agreements }
                if (-not $hasTesseract) { winget install --id UB-Mannheim.TesseractOCR -e --silent --accept-source-agreements --accept-package-agreements }
            }
        }
    } else {
        Log-Warn "Winget non disponible. Veuillez installer manuellement FFmpeg et Tesseract si vous prévoyez l'utilisation de l'enregistrement vidéo et de l'OCR."
    }
} else {
    Log-Success "Tous les utilitaires système recommandés sont disponibles."
}

# Step 3: Check & Install Astral UV
Log-Info "3/5 - Vérification du gestionnaire Astral 'uv'..."
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
$uvPath = if ($uvCmd) { $uvCmd.Source } else { Join-Path $env:USERPROFILE ".local\bin\uv.exe" }

if (-not (Test-Path $uvPath) -and -not $uvCmd) {
    Log-Info "'uv' n'a pas été détecté. Installation via le script officiel Astral..."
    if ($DryRun) {
        Log-Info "[Dry-Run] powershell -ExecutionPolicy ByPass -c `"irm https://astral.sh/uv/install.ps1 | iex`""
    } else {
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
    }
}

if (-not $DryRun) {
    $uvExec = Get-Command uv -ErrorAction SilentlyContinue
    if (-not $uvExec -and (Test-Path $uvPath)) {
        $uvExecName = $uvPath
    } elseif ($uvExec) {
        $uvExecName = "uv"
    } else {
        Log-Error "Échec de détection d'Astral 'uv'. Veuillez l'installer depuis https://astral.sh/uv"
        exit 1
    }
    $uvVer = & $uvExecName --version
    Log-Success "Astral uv opérationnel : $uvVer"
} else {
    $uvExecName = "uv"
}

# Step 4: Install GUI Agent via `uv tool install`
Log-Info "4/5 - Installation isolée de 'gui-agent' via 'uv tool install'..."
$scriptDir = $PSScriptRoot
if ($Local -or (Test-Path (Join-Path $scriptDir "pyproject.toml"))) {
    Log-Info "Installation en mode local depuis $scriptDir..."
    if (-not $DryRun) {
        & $uvExecName tool install "$scriptDir" --force
    } else {
        Log-Info "[Dry-Run] uv tool install `"$scriptDir`" --force"
    }
} else {
    Log-Info "Installation depuis le registre de packages..."
    if (-not $DryRun) {
        try {
            & $uvExecName tool install gui-agent --force
        } catch {
            Log-Info "Installation depuis le dépôt Git distant..."
            & $uvExecName tool install "git+https://github.com/leandre755/gui_agent.git" --force
        }
    } else {
        Log-Info "[Dry-Run] uv tool install gui-agent --force"
    }
}

if (-not $DryRun) {
    $localBin = Join-Path $env:USERPROFILE ".local\bin"
    if ($env:Path -notlike "*$localBin*") {
        $env:Path = "$localBin;$env:Path"
    }
    Log-Success "Exécutables 'gui-agent.exe' et 'mcp-gui-server.exe' installés dans $localBin !"
}

# Step 5: Configure MCP Clients
Log-Info "5/5 - Configuration des clients MCP..."
if ($SkipMcpConfig -or $DryRun) {
    Log-Info "Configuration des clients MCP ignorée."
} else {
    # 1. Claude Code CLI
    $claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
    if ($claudeCmd) {
        Log-Info "Claude Code CLI détecté."
        $configClaude = $true
        if (-not $Yes) {
            $resp = Read-Host "Voulez-vous enregistrer automatiquement gui-agent dans Claude Code ? [O/n]"
            if ($resp -notmatch "^(o|oui|y|yes|)$") { $configClaude = $false }
        }
        if ($configClaude) {
            try {
                & claude mcp add gui-agent -- gui-agent
                Log-Success "Serveur MCP configuré pour Claude Code."
            } catch {
                Log-Warn "Le serveur est peut-être déjà configuré dans Claude Code."
            }
        }
    }

    # 2. Antigravity CLI Config
    $geminiDir = Join-Path $env:USERPROFILE ".gemini\config"
    $geminiConfigFile = Join-Path $geminiDir "mcp_config.json"
    if (Test-Path (Join-Path $env:USERPROFILE ".gemini")) {
        Log-Info "Environnement Antigravity CLI détecté."
        if (-not (Test-Path $geminiDir)) {
            New-Item -ItemType Directory -Path $geminiDir -Force | Out-Null
        }

        $configData = @{ mcpServers = @{} }
        if (Test-Path $geminiConfigFile) {
            try {
                $rawJson = Get-Content -Path $geminiConfigFile -Raw -Encoding UTF8
                $parsed = $rawJson | ConvertFrom-Json
                if ($parsed.mcpServers) {
                    $configData.mcpServers = $parsed.mcpServers
                }
            } catch {
                Log-Warn "Réinitialisation du fichier mcp_config.json corrompu."
            }
        }

        $configData.mcpServers."gui-agent" = @{
            command = "gui-agent"
            args = @()
        }

        $configData | ConvertTo-Json -Depth 5 | Set-Content -Path $geminiConfigFile -Encoding UTF8
        Log-Success "Configuration Antigravity CLI mise à jour dans $geminiConfigFile"
    }
}

Write-Host ""
Write-Color "============================================================" "Green"
Write-Color "       Installation de GUI Agent terminée avec succès !    " "Green"
Write-Color "============================================================" "Green"
Write-Host ""
Write-Host "Commandes disponibles dans PowerShell / Terminal :"
Write-Color "  • gui-agent       : Lance le serveur FastMCP en mode stdio" "Cyan"
Write-Color "  • mcp-gui-server  : Alias de compatibilité pour le serveur stdio" "Cyan"
Write-Host ""
Write-Host "Pour vérifier l'installation :"
Write-Color "  uv tool list" "Yellow"
Write-Host ""
