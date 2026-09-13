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
            if ($LASTEXITCODE -eq 0) {
                Log-Success "Outil 'gui-agent' désinstallé avec succès de uv."
            } else {
                Log-Warn "Le package 'gui-agent' n'était pas présent dans les outils uv ou code de sortie : $LASTEXITCODE."
            }
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
            if ($LASTEXITCODE -eq 0) {
                Log-Success "Configuration Claude Code nettoyée."
            } else {
                Log-Warn "Le serveur MCP n'était pas enregistré dans Claude Code ou code de sortie : $LASTEXITCODE."
            }
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
                $jsonOut = $parsed | ConvertTo-Json -Depth 10
                [System.IO.File]::WriteAllText($geminiConfigFile, $jsonOut, (New-Object System.Text.UTF8Encoding($false)))
                Log-Success "Entrée 'gui-agent' retirée de $geminiConfigFile"
            }
        } catch {
            Log-Warn "Impossible de modifier $geminiConfigFile : $_"
        }
    }
}

# Step 3: Purge Screenshots and Runtime Cache
Log-Info "3/3 - Nettoyage des données temporaires et captures d'écran..."
$dataDirs = @(
    (Join-Path $env:LOCALAPPDATA "gui-agent"),
    (Join-Path $env:USERPROFILE ".local\share\gui-agent")
)

$targetDirs = @()
foreach ($dir in $dataDirs) {
    if (Test-Path $dir) {
        $targetDirs += $dir
    }
}

if ($targetDirs.Count -gt 0) {
    if ($DryRun) {
        foreach ($dir in $targetDirs) {
            Log-Info "[Dry-Run] Purge possible du répertoire : $dir"
        }
    } else {
        $doPurge = $false
        if ($PurgeData) {
            $doPurge = $true
        } elseif (-not $Yes) {
            $resp = Read-Host "Voulez-vous supprimer définitivement les données et captures résiduelles ($($targetDirs -join ', ')) ? [o/N]"
            if ($resp -match "^(o|oui|y|yes)$") { $doPurge = $true }
        }

        if ($doPurge) {
            foreach ($dir in $targetDirs) {
                try {
                    Remove-Item -Path $dir -Recurse -Force
                    if (Test-Path $dir) {
                        Log-Warn "Impossible de supprimer complètement : $dir (fichiers verrouillés ou droits insuffisants)"
                    } else {
                        Log-Success "Données et captures supprimées avec succès : $dir"
                    }
                } catch {
                    Log-Warn "Erreur lors de la suppression de $dir : $_"
                }
            }
        } else {
            foreach ($dir in $targetDirs) {
                Log-Info "Données conservées : $dir"
            }
        }
    }
} else {
    Log-Info "Aucun dossier de données résiduelles trouvé."
}

Write-Host ""
Write-Color "============================================================" "Green"
Write-Color "     Désinstallation de GUI Agent terminée avec succès !    " "Green"
Write-Color "============================================================" "Green"
Write-Host ""
