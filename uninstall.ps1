# ==============================================================================
# GUI Agent - Automated Windows Uninstallation Script (PowerShell)
# Method: Clean removal of uv tool, MCP configurations, and optional data purge
# ==============================================================================

[CmdletBinding()]
param(
    [Alias("y", "no-prompt")]
    [switch]$Yes,

    [Alias("p")]
    [switch]$PurgeData,

    [Alias("d")]
    [switch]$DryRun
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
    Write-Color "     GUI Agent - Clean Uninstaller (Windows PowerShell)     " "Cyan"
    Write-Color "============================================================" "Cyan"
    Write-Host ""
}

Print-Banner

# Step 1: Environment Check
Log-Info "1/3 - Désinstallation du package 'gui-agent' via Astral 'uv'..."
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
$uvPath = if ($uvCmd) { $uvCmd.Source } else { Join-Path $env:USERPROFILE ".local\bin\uv.exe" }

if ($uvCmd -or (Test-Path $uvPath)) {
    $uvExec = if ($uvCmd) { "uv" } else { $uvPath }
    if ($DryRun) {
        Log-Info "[Dry-Run] $uvExec tool uninstall gui-agent"
    } else {
        try {
            & $uvExec tool uninstall gui-agent
            Log-Success "Outil 'gui-agent' désinstallé avec succès de uv."
        } catch {
            Log-Warn "Le package 'gui-agent' n'était pas présent dans les outils uv."
        }
    }
} else {
    Log-Warn "Gestionnaire 'uv' non détecté. Aucun outil uv à désinstaller."
}

# Step 2: Remove MCP Client Registrations
Log-Info "2/3 - Nettoyage des configurations des clients MCP..."
if ($DryRun) {
    Log-Info "[Dry-Run] claude mcp remove gui-agent"
    Log-Info "[Dry-Run] Suppression de l'entrée 'gui-agent' dans %USERPROFILE%\.gemini\config\mcp_config.json"
} else {
    # 1. Claude Code CLI
    $claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
    if ($claudeCmd) {
        try {
            & claude mcp remove gui-agent
            Log-Success "Configuration Claude Code nettoyée."
        } catch {
            Log-Warn "Le serveur MCP n'était pas enregistré dans Claude Code."
        }
    }

    # 2. Antigravity CLI Config
    $geminiConfigFile = Join-Path $env:USERPROFILE ".gemini\config\mcp_config.json"
    if (Test-Path $geminiConfigFile) {
        try {
            $rawJson = Get-Content -Path $geminiConfigFile -Raw -Encoding UTF8
            $parsed = $rawJson | ConvertFrom-Json
            if ($parsed.mcpServers -and $parsed.mcpServers."gui-agent") {
                $parsed.mcpServers.PSObject.Properties.Remove("gui-agent")
                $parsed | ConvertTo-Json -Depth 5 | Set-Content -Path $geminiConfigFile -Encoding UTF8
                Log-Success "Entrée 'gui-agent' retirée de $geminiConfigFile"
            }
        } catch {
            Log-Warn "Impossible de modifier $geminiConfigFile : $_"
        }
    }
}

# Step 3: Purge Screenshots and Runtime Cache
Log-Info "3/3 - Nettoyage des données temporaires et captures d'écran..."
$screenshotsDir = Join-Path $env:USERPROFILE ".local\share\gui-agent\screenshots"

if (Test-Path $screenshotsDir) {
    if ($DryRun) {
        Log-Info "[Dry-Run] Purge possible du répertoire : $screenshotsDir"
    } else {
        $doPurge = $false
        if ($PurgeData) {
            $doPurge = $true
        } elseif (-not $Yes) {
            $resp = Read-Host "Voulez-vous supprimer définitivement le dossier de captures ($screenshotsDir) ? [o/N]"
            if ($resp -match "^(o|oui|y|yes)$") { $doPurge = $true }
        }

        if ($doPurge) {
            Remove-Item -Path $screenshotsDir -Recurse -Force -ErrorAction SilentlyContinue
            Log-Success "Dossier de captures supprimé : $screenshotsDir"
        } else {
            Log-Info "Dossier de captures conservé : $screenshotsDir"
        }
    }
} else {
    Log-Info "Aucun dossier de capture résiduel trouvé."
}

Write-Host ""
Write-Color "============================================================" "Green"
Write-Color "     Désinstallation de GUI Agent terminée avec succès !    " "Green"
Write-Color "============================================================" "Green"
Write-Host ""
