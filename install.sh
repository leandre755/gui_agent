#!/usr/bin/env bash
# ==============================================================================
# GUI Agent - Automated Installation Script (Linux)
# Method: Isolated installation via Astral `uv tool install`
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
LOCAL_INSTALL=false
SKIP_MCP_CONFIG=false
PACKAGE_NAME="gui-agent"
GIT_REPO_URL="https://github.com/leandre755/gui_agent.git"

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
    echo "       GUI Agent - FastMCP Linux Desktop Server            "
    echo "           Automated Production Installer                   "
    echo "============================================================"
    echo -e "${NC}"
}

show_help() {
    print_banner
    echo "Usage: ./install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -y, --yes, --no-prompt   Non-interactive mode (accept all defaults)"
    echo "  -d, --dry-run            Check prerequisites without modifying system"
    echo "  -l, --local              Force installation from local directory"
    echo "  --skip-mcp-config        Skip Claude Code and Antigravity MCP configuration"
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
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -l|--local)
            LOCAL_INSTALL=true
            shift
            ;;
        --skip-mcp-config)
            SKIP_MCP_CONFIG=true
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

# Step 1: OS Verification
log_info "1/5 - Vérification de l'environnement d'exécution..."
OS_TYPE="$(uname -s)"
if [[ "$OS_TYPE" != "Linux" ]]; then
    log_error "GUI Agent nécessite un environnement de bureau Linux (X11 / XWayland). Détecté: $OS_TYPE"
    exit 1
fi
log_success "Système d'exploitation compatible : Linux ($(uname -m))"

# Step 2: System Dependencies Verification
log_info "2/5 - Vérification des dépendances système Linux (X11 / Capture / OCR)..."
MISSING_SYS_DEPS=()

check_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        MISSING_SYS_DEPS+=("$1")
    fi
}

check_cmd "xdotool"
check_cmd "wmctrl"
check_cmd "ffmpeg"
check_cmd "xclip"

# Spectacle ou scrot pour la capture
if ! command -v "spectacle" >/dev/null 2>&1 && ! command -v "scrot" >/dev/null 2>&1 && ! command -v "import" >/dev/null 2>&1; then
    MISSING_SYS_DEPS+=("spectacle (ou scrot)")
fi

# Tesseract pour l'OCR
if ! command -v "tesseract" >/dev/null 2>&1; then
    MISSING_SYS_DEPS+=("tesseract-ocr")
fi

if [[ ${#MISSING_SYS_DEPS[@]} -gt 0 ]]; then
    log_warn "Dépendances système manquantes détectées : ${MISSING_SYS_DEPS[*]}"
    
    # Détection du gestionnaire de paquets
    INSTALL_CMD=""
    if command -v apt-get >/dev/null 2>&1; then
        INSTALL_CMD="sudo apt-get update && sudo apt-get install -y xdotool wmctrl spectacle ffmpeg xclip tesseract-ocr"
    elif command -v dnf >/dev/null 2>&1; then
        INSTALL_CMD="sudo dnf install -y xdotool wmctrl spectacle ffmpeg xclip tesseract"
    elif command -v pacman >/dev/null 2>&1; then
        INSTALL_CMD="sudo pacman -S --needed xdotool wmctrl spectacle ffmpeg xclip tesseract"
    fi

    if [[ -n "$INSTALL_CMD" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[Dry-Run] Commande système recommandée : $INSTALL_CMD"
        elif [[ "$NON_INTERACTIVE" == "true" ]]; then
            log_info "Installation automatique des dépendances système..."
            eval "$INSTALL_CMD" || log_warn "Échec d'installation avec sudo, poursuite de l'installation..."
        else
            echo -e "${YELLOW}Voulez-vous installer automatiquement les paquets système manquants ? [O/n]${NC} "
            read -r response
            if [[ "$response" =~ ^([oO][uU][iI]|[oO]|"")$ ]]; then
                eval "$INSTALL_CMD" || log_warn "Échec lors de l'installation automatique. Poursuite..."
            else
                log_warn "Poursuite sans installer les paquets système. Certaines fonctionnalités GUI pourront être limitées."
            fi
        fi
    else
        log_warn "Gestionnaire de paquets non reconnu. Veuillez installer manuellement : ${MISSING_SYS_DEPS[*]}"
    fi
else
    log_success "Toutes les dépendances système Linux requises sont présentes."
fi

# Step 3: UV Package Manager Verification / Installation
log_info "3/5 - Vérification du gestionnaire Astral 'uv'..."
UV_PATH="$(command -v uv 2>/dev/null || echo "${HOME}/.local/bin/uv")"

if [[ ! -x "$UV_PATH" ]]; then
    log_info "'uv' n'a pas été trouvé. Installation automatique via le script officiel Astral..."
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[Dry-Run] curl -LsSf https://astral.sh/uv/install.sh | sh"
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="${HOME}/.local/bin:${PATH}"
        UV_PATH="${HOME}/.local/bin/uv"
    fi
fi

if [[ "$DRY_RUN" != "true" ]]; then
    if [[ ! -x "$UV_PATH" ]]; then
        log_error "Impossible de trouver ou d'exécuter 'uv'. Veuillez l'installer manuellement : https://astral.sh/uv"
        exit 1
    fi
    UV_VERSION="$("$UV_PATH" --version)"
    log_success "Astral uv opérationnel : $UV_VERSION"
fi

# Ensure ~/.local/bin is on PATH in current subshell
export PATH="${HOME}/.local/bin:${PATH}"

# Step 4: Tool Installation via `uv tool install`
log_info "4/5 - Installation isolée du package '$PACKAGE_NAME' via 'uv tool install'..."

if [[ "$DRY_RUN" == "true" ]]; then
    log_info "[Dry-Run] uv tool install --force $PACKAGE_NAME"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ "$LOCAL_INSTALL" == "true" ]] || [[ -f "${SCRIPT_DIR}/pyproject.toml" && -d "${SCRIPT_DIR}/gui_agent" ]]; then
        log_info "Installation locale depuis : $SCRIPT_DIR"
        "$UV_PATH" tool install "$SCRIPT_DIR" --force
    else
        # Tentative depuis PyPI avec fallback sur Git repo
        log_info "Installation depuis le registre de packages..."
        if ! "$UV_PATH" tool install "$PACKAGE_NAME" --force 2>/dev/null; then
            log_info "Package PyPI non encore publié ou inaccessible. Installation directe depuis le dépôt Git..."
            "$UV_PATH" tool install "git+${GIT_REPO_URL}" --force
        fi
    fi

    # Vérification des commandes installées
    if command -v gui-agent >/dev/null 2>&1 || [[ -x "${HOME}/.local/bin/gui-agent" ]]; then
        log_success "Exécutables 'gui-agent' et 'mcp-gui-server' installés avec succès dans ~/.local/bin !"
    else
        log_warn "Les exécutables ont été installés mais ~/.local/bin n'est pas encore dans votre PATH."
        log_warn "Ajoutez 'export PATH=\"\$HOME/.local/bin:\$PATH\"' dans votre ~/.bashrc ou ~/.zshrc."
    fi
fi

# Step 5: MCP Client Automatic Configuration
log_info "5/5 - Configuration des clients MCP..."

if [[ "$SKIP_MCP_CONFIG" == "true" || "$DRY_RUN" == "true" ]]; then
    log_info "Configuration des clients MCP ignorée (--skip-mcp-config ou --dry-run)."
else
    # 1. Claude Code CLI Integration
    if command -v claude >/dev/null 2>&1; then
        log_info "Client Claude Code CLI détecté."
        CONFIGURE_CLAUDE=true
        if [[ "$NON_INTERACTIVE" != "true" ]]; then
            echo -e "${YELLOW}Voulez-vous enregistrer automatiquement gui-agent dans Claude Code CLI ? [O/n]${NC} "
            read -r response
            if [[ ! "$response" =~ ^([oO][uU][iI]|[oO]|"")$ ]]; then
                CONFIGURE_CLAUDE=false
            fi
        fi

        if [[ "$CONFIGURE_CLAUDE" == "true" ]]; then
            log_info "Enregistrement dans Claude Code : claude mcp add gui-agent -- gui-agent"
            claude mcp add gui-agent -- gui-agent 2>/dev/null || log_warn "Claude MCP add a retourné un statut non nul (le serveur est peut-être déjà configuré)."
            log_success "Serveur MCP configuré pour Claude Code."
        fi
    fi

    # 2. Antigravity CLI Integration (~/.gemini/config/mcp_config.json)
    ANTIGRAVITY_CONFIG_DIR="${HOME}/.gemini/config"
    ANTIGRAVITY_CONFIG_FILE="${ANTIGRAVITY_CONFIG_DIR}/mcp_config.json"
    if [[ -d "${HOME}/.gemini" ]]; then
        log_info "Environnement Antigravity CLI détecté."
        mkdir -p "$ANTIGRAVITY_CONFIG_DIR"
        
        # Injection / fusion sécurisée dans mcp_config.json via python
        "$UV_PATH" run python - <<EOF
import json
import os

config_path = "$ANTIGRAVITY_CONFIG_FILE"
data = {"mcpServers": {}}

if os.path.exists(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "mcpServers" not in data:
                data["mcpServers"] = {}
    except Exception:
        data = {"mcpServers": {}}

data["mcpServers"]["gui-agent"] = {
    "command": "gui-agent",
    "args": [],
    "env": {
        "DISPLAY": os.environ.get("DISPLAY", ":0")
    }
}

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
EOF
        log_success "Configuration Antigravity CLI mise à jour dans $ANTIGRAVITY_CONFIG_FILE"
    fi
fi

echo ""
echo -e "${GREEN}${BOLD}============================================================${NC}"
echo -e "${GREEN}${BOLD}       Installation de GUI Agent terminée avec succès !    ${NC}"
echo -e "${GREEN}${BOLD}============================================================${NC}"
echo ""
echo -e "Commandes disponibles :"
echo -e "  • ${CYAN}gui-agent${NC}       : Lance le serveur FastMCP en mode stdio"
echo -e "  • ${CYAN}mcp-gui-server${NC}  : Alias de compatibilité pour le serveur stdio"
echo ""
echo -e "Pour vérifier l'installation :"
echo -e "  ${BOLD}uv tool list${NC}"
echo ""
