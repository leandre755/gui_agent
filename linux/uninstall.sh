#!/usr/bin/env bash
# ==============================================================================
# GUI Agent - Automated Uninstallation Script (Linux / macOS)
# Method: Clean removal of uv tool, MCP registrations, and optional data purge
# ==============================================================================

set -euo pipefail

# ANSI Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Default options
NON_INTERACTIVE=false
DRY_RUN=false
PURGE_DATA=false
PACKAGE_NAME="gui-agent"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "============================================================"
    echo "       GUI Agent - Clean Uninstaller (Linux / macOS)        "
    echo "============================================================"
    echo -e "${NC}"
}

show_help() {
    print_banner
    echo "Usage: ./linux/uninstall.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -y, --yes, --no-prompt   Non-interactive mode (accept defaults)"
    echo "  -p, --purge-data         Purge generated screenshots and runtime data"
    echo "  -d, --dry-run            Show uninstallation steps without modifying system"
    echo "  -h, --help               Show this help message and exit"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -y|--yes|--no-prompt)
            NON_INTERACTIVE=true
            shift
            ;;
        -p|--purge-data)
            PURGE_DATA=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Option inconnue : $1"
            show_help
            exit 1
            ;;
    esac
done

print_banner

# Step 1: Remove Isolated uv tool
log_info "1/3 - Désinstallation du package '$PACKAGE_NAME' via Astral 'uv'..."
UV_PATH="$(command -v uv 2>/dev/null || echo "${HOME}/.local/bin/uv")"

if [[ -x "$UV_PATH" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[Dry-Run] $UV_PATH tool uninstall $PACKAGE_NAME"
    else
        set +e
        UV_OUT="$("$UV_PATH" tool uninstall "$PACKAGE_NAME" 2>&1)"
        UV_STATUS=$?
        set -e
        if [[ $UV_STATUS -eq 0 ]]; then
            log_success "Outil '$PACKAGE_NAME' désinstallé avec succès de uv."
        elif echo "$UV_OUT" | grep -qiE "not installed|not found"; then
            log_info "Package '$PACKAGE_NAME' n'était pas présent dans les outils uv."
        else
            log_warn "Échec de désinstallation de l'outil uv : $UV_OUT"
        fi
    fi
else
    log_warn "Gestionnaire 'uv' non détecté. Aucun outil uv à désinstaller."
fi

# Nettoyage du binaire autonome du médiateur AT-SPI Rust dans ~/.local/bin s'il existe
STANDALONE_ATSPI_BIN="${HOME}/.local/bin/gui-agent-atspi"
if [[ -f "$STANDALONE_ATSPI_BIN" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[Dry-Run] Suppression du binaire autonome : $STANDALONE_ATSPI_BIN"
    else
        rm -f "$STANDALONE_ATSPI_BIN"
        log_success "Binaire autonome du médiateur AT-SPI supprimé : $STANDALONE_ATSPI_BIN"
    fi
fi

# Step 2: Remove MCP Client Registrations
log_info "2/3 - Nettoyage des configurations des clients MCP..."

if [[ "$DRY_RUN" == "true" ]]; then
    log_info "[Dry-Run] claude mcp remove gui-agent"
    log_info "[Dry-Run] Suppression de l'entrée 'gui-agent' dans ~/.gemini/config/mcp_config.json"
else
    # 1. Claude Code CLI
    if command -v claude >/dev/null 2>&1; then
        log_info "Suppression du serveur MCP dans Claude Code..."
        if claude mcp remove "$PACKAGE_NAME" 2>/dev/null; then
            log_success "Configuration Claude Code nettoyée."
        else
            log_warn "Échec de suppression de la configuration Claude Code (le serveur n'était peut-être pas configuré)."
        fi
    fi

    # 2. Antigravity CLI Config (~/.gemini/config/mcp_config.json)
    ANTIGRAVITY_CONFIG_FILE="${HOME}/.gemini/config/mcp_config.json"
    if [[ -f "$ANTIGRAVITY_CONFIG_FILE" ]]; then
        log_info "Nettoyage de la configuration Antigravity CLI..."
        if [[ -x "$UV_PATH" ]]; then
            if "$UV_PATH" run python - <<EOF
import json
import os
import sys
import tempfile

config_path = "$ANTIGRAVITY_CONFIG_FILE"
if os.path.exists(config_path):
    tmp_name = None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "mcpServers" in data and "$PACKAGE_NAME" in data["mcpServers"]:
            del data["mcpServers"]["$PACKAGE_NAME"]
            config_dir = os.path.dirname(config_path)
            with tempfile.NamedTemporaryFile("w", dir=config_dir, delete=False, encoding="utf-8") as tmp_f:
                tmp_name = tmp_f.name
                json.dump(data, tmp_f, indent=2, ensure_ascii=False)
                tmp_f.write("\n")
                tmp_f.flush()
                os.fsync(tmp_f.fileno())
            os.replace(tmp_name, config_path)
            print("Antigravity config updated successfully.")
    except Exception as e:
        if tmp_name and os.path.exists(tmp_name):
            try:
                os.remove(tmp_name)
            except OSError:
                pass
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
EOF
            then
                log_success "Entrée '$PACKAGE_NAME' retirée de $ANTIGRAVITY_CONFIG_FILE"
            else
                log_warn "Échec de mise à jour de $ANTIGRAVITY_CONFIG_FILE"
            fi
        fi
    fi
fi

# Step 3: Purge Screenshots and Runtime Cache
log_info "3/3 - Nettoyage des données temporaires et captures d'écran..."
# Pour la purge destructive, ignorer tout override d'environnement arbitraire afin d'éviter la suppression récursive de répertoires tiers
CACHE_BASE="${XDG_CACHE_HOME:-${HOME}/.cache}"
SCREENSHOTS_DIR="${CACHE_BASE}/gui-agent/screenshots"

if [[ -d "$SCREENSHOTS_DIR" ]]; then
    CANONICAL_DIR="$(cd "$SCREENSHOTS_DIR" 2>/dev/null && pwd -P || true)"
    REAL_HOME="$(cd "${HOME}" 2>/dev/null && pwd -P || echo "${HOME}")"
    REAL_CACHE="$(cd "${CACHE_BASE}" 2>/dev/null && pwd -P || echo "${CACHE_BASE}")"

    # Vérification stricte : le répertoire à supprimer doit impérativement être un sous-dossier gui-agent approuvé
    if [[ -z "$CANONICAL_DIR" || "$CANONICAL_DIR" == "/" || "$CANONICAL_DIR" == "$REAL_HOME" || "$CANONICAL_DIR" == "$REAL_CACHE" || "$CANONICAL_DIR" == "/tmp" || "$CANONICAL_DIR" == "/var" ]]; then
        log_error "Chemin de captures d'écran non sécurisé détecté : $SCREENSHOTS_DIR. Purge annulée."
    elif [[ "$CANONICAL_DIR" != *"/gui-agent/screenshots"* && "$CANONICAL_DIR" != *"/gui-agent" ]]; then
        log_error "Le répertoire ($CANONICAL_DIR) n'appartient pas au cache approuvé de gui-agent. Purge annulée par sécurité."
    elif [[ "$DRY_RUN" == "true" ]]; then
        log_info "[Dry-Run] Purge possible du répertoire de captures : $CANONICAL_DIR"
    else
        DO_PURGE=false
        if [[ "$PURGE_DATA" == "true" ]]; then
            DO_PURGE=true
        elif [[ "$NON_INTERACTIVE" != "true" ]]; then
            echo -e "${YELLOW}Voulez-vous supprimer définitivement le répertoire de captures ($CANONICAL_DIR) ? [o/N]${NC} "
            response=""
            read -r response || response="n"
            if [[ "$response" =~ ^([oO][uU][iI]|[oO])$ ]]; then
                DO_PURGE=true
            fi
        fi

        if [[ "$DO_PURGE" == "true" ]]; then
            rm -rf -- "$CANONICAL_DIR"
            log_success "Répertoire de captures supprimé : $CANONICAL_DIR"
        else
            log_info "Répertoire de captures conservé : $CANONICAL_DIR"
        fi
    fi
else
    log_info "Aucun répertoire de capture résiduel trouvé."
fi

echo ""
echo -e "${GREEN}${BOLD}============================================================${NC}"
echo -e "${GREEN}${BOLD}     Désinstallation de GUI Agent terminée avec succès !    ${NC}"
echo -e "${GREEN}${BOLD}============================================================${NC}"
echo ""
