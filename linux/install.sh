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
    echo "Usage: ./linux/install.sh [OPTIONS]"
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

python3 -c "import dbus" >/dev/null 2>&1 || MISSING_SYS_DEPS+=("python3-dbus")
python3 -c "import tkinter" >/dev/null 2>&1 || MISSING_SYS_DEPS+=("python3-tk")
pkg-config --exists atspi-2 2>/dev/null || [ -d "/usr/include/at-spi-2.0" ] || command -v at-spi-bus-launcher >/dev/null 2>&1 || MISSING_SYS_DEPS+=("at-spi2-core")
command -v cargo >/dev/null 2>&1 || MISSING_SYS_DEPS+=("cargo")
if [[ ${#MISSING_SYS_DEPS[@]} -gt 0 ]]; then
    log_warn "Dépendances système manquantes détectées : ${MISSING_SYS_DEPS[*]}"
    
    # Détection du gestionnaire de paquets
    INSTALL_CMD=""
    if command -v apt-get >/dev/null 2>&1; then
        INSTALL_CMD="sudo apt-get update && sudo apt-get install -y xdotool wmctrl spectacle ffmpeg xclip tesseract-ocr python3-dbus at-spi2-core python3-tk cargo"
    elif command -v dnf >/dev/null 2>&1; then
        INSTALL_CMD="sudo dnf install -y xdotool wmctrl spectacle ffmpeg xclip tesseract python3-dbus at-spi2-core python3-tkinter cargo"
    elif command -v pacman >/dev/null 2>&1; then
        INSTALL_CMD="sudo pacman -S --needed --noconfirm xdotool wmctrl spectacle ffmpeg xclip tesseract python-dbus at-spi2-core tk rust"
    fi

    if [[ -n "$INSTALL_CMD" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[Dry-Run] Commande système recommandée : $INSTALL_CMD"
        elif [[ "$NON_INTERACTIVE" == "true" ]]; then
            log_info "Installation automatique des dépendances système..."
            eval "$INSTALL_CMD" || log_warn "Échec d'installation avec sudo, poursuite de l'installation..."
        elif [[ ! -t 0 ]]; then
            log_warn "Entrée standard non interactive sans flag -y/--yes. Poursuite sans installer les paquets système."
        else
            echo -e "${YELLOW}Voulez-vous installer automatiquement les paquets système manquants ? [O/n]${NC} "
            response=""
            read -r response || response="n"
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
    log_info "[Dry-Run] cargo build --release --manifest-path crates/atspi_mediator/Cargo.toml (si cargo est présent)"
else
    SCRIPT_DIR=""
    if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    fi

    PROJECT_DIR=""
    if [[ -n "$SCRIPT_DIR" ]]; then
        if [[ -f "${SCRIPT_DIR}/pyproject.toml" ]]; then
            PROJECT_DIR="$SCRIPT_DIR"
        elif [[ -f "$(dirname "$SCRIPT_DIR")/pyproject.toml" ]]; then
            PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
        fi
    fi

    if [[ "$LOCAL_INSTALL" == "true" && -n "$PROJECT_DIR" ]] || [[ -n "$PROJECT_DIR" && -f "${PROJECT_DIR}/pyproject.toml" ]]; then
        log_info "Installation locale depuis : $PROJECT_DIR"
        "$UV_PATH" tool install "$PROJECT_DIR" --force
    else
        # Tentative depuis PyPI avec fallback sur Git repo
        log_info "Installation depuis le registre de packages..."
        if ! "$UV_PATH" tool install "$PACKAGE_NAME" --force 2>/dev/null; then
            log_info "Package PyPI non encore publié ou inaccessible. Installation directe depuis le dépôt Git..."
            "$UV_PATH" tool install "git+${GIT_REPO_URL}" --force
        fi
    fi

    # Compilation et installation du médiateur AT-SPI Rust si Cargo est présent
    if command -v cargo >/dev/null 2>&1; then
        log_info "Compilation et installation du médiateur natif AT-SPI Rust (gui-agent-atspi)..."
        mkdir -p "${HOME}/.local/bin"
        if [[ -n "$PROJECT_DIR" && -d "$PROJECT_DIR" ]]; then
            mkdir -p "${PROJECT_DIR}/linux/bin" 2>/dev/null || true
        fi

        WORKSPACE_CARGO_PATH="${PROJECT_DIR:+$PROJECT_DIR/Cargo.toml}"
        CARGO_TOML_PATH="${PROJECT_DIR:+$PROJECT_DIR/linux/crates/atspi_mediator/Cargo.toml}"
        if [[ -n "$PROJECT_DIR" && ! -f "$CARGO_TOML_PATH" ]]; then
            CARGO_TOML_PATH="${PROJECT_DIR}/crates/atspi_mediator/Cargo.toml"
        fi

        TARGET_DIR="${PROJECT_DIR:+$PROJECT_DIR/target}"
        if [[ -z "$TARGET_DIR" ]]; then
            TARGET_DIR="$(mktemp -d /tmp/gui-agent-cargo-target-XXXXXX)"
        fi
        mkdir -p "$TARGET_DIR"

        if [[ -n "$WORKSPACE_CARGO_PATH" && -f "$WORKSPACE_CARGO_PATH" ]]; then
            if CARGO_TARGET_DIR="$TARGET_DIR" cargo build --release --manifest-path "$WORKSPACE_CARGO_PATH" --bin gui-agent-atspi; then
                if [[ -f "${TARGET_DIR}/release/gui-agent-atspi" ]]; then
                    cp "${TARGET_DIR}/release/gui-agent-atspi" "${HOME}/.local/bin/gui-agent-atspi"
                    if [[ -n "$PROJECT_DIR" && -d "$PROJECT_DIR" ]]; then
                        cp "${TARGET_DIR}/release/gui-agent-atspi" "${PROJECT_DIR}/linux/bin/gui-agent-atspi" 2>/dev/null || true
                        chmod +x "${PROJECT_DIR}/linux/bin/gui-agent-atspi" 2>/dev/null || true
                    fi
                    chmod +x "${HOME}/.local/bin/gui-agent-atspi" 2>/dev/null || true
                    log_success "Médiateur AT-SPI natif compilé et installé avec succès dans ~/.local/bin/gui-agent-atspi"
                else
                    log_warn "Binaire compilé introuvable dans ${TARGET_DIR}/release. Le fallback Python/D-Bus sera utilisé."
                fi
            else
                log_warn "Échec de la compilation Cargo du médiateur natif AT-SPI. Le fallback Python/D-Bus sera utilisé."
            fi
        elif [[ -n "$CARGO_TOML_PATH" && -f "$CARGO_TOML_PATH" ]]; then
            if CARGO_TARGET_DIR="$TARGET_DIR" cargo build --release --manifest-path "$CARGO_TOML_PATH"; then
                if [[ -f "${TARGET_DIR}/release/gui-agent-atspi" ]]; then
                    cp "${TARGET_DIR}/release/gui-agent-atspi" "${HOME}/.local/bin/gui-agent-atspi"
                    if [[ -n "$PROJECT_DIR" && -d "$PROJECT_DIR" ]]; then
                        cp "${TARGET_DIR}/release/gui-agent-atspi" "${PROJECT_DIR}/linux/bin/gui-agent-atspi" 2>/dev/null || true
                        chmod +x "${PROJECT_DIR}/linux/bin/gui-agent-atspi" 2>/dev/null || true
                    fi
                    chmod +x "${HOME}/.local/bin/gui-agent-atspi" 2>/dev/null || true
                    log_success "Médiateur AT-SPI natif installé avec succès dans ~/.local/bin/gui-agent-atspi"
                else
                    log_warn "Binaire compilé introuvable après build. Le fallback Python/D-Bus sera utilisé."
                fi
            else
                log_warn "Échec de la compilation Cargo du médiateur natif AT-SPI. Le fallback Python/D-Bus sera utilisé."
            fi
        else
            # Cas d'une installation distante (curl | bash) sans clone local du dépôt
            log_info "Dépôt local non détecté, installation du médiateur natif depuis Git (${GIT_REPO_URL})..."
            if cargo install --git "${GIT_REPO_URL}" atspi-mediator --root "${HOME}/.local" --force; then
                chmod +x "${HOME}/.local/bin/gui-agent-atspi" 2>/dev/null || true
                log_success "Médiateur AT-SPI natif installé depuis Git dans ~/.local/bin/gui-agent-atspi"
            else
                log_warn "Échec de l'installation de gui-agent-atspi depuis Git. L'accessibilité AT-SPI utilisera le fallback Python/D-Bus."
            fi
        fi
    else
        log_warn "Cargo (Rust) non détecté : le binaire d'accessibilité 'gui-agent-atspi' ne sera pas compilé."
        log_warn "Pour bénéficier de l'accessibilité AT-SPI native : curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    fi

    # Vérification des commandes installées
    INSTALLED_BINS=()
    if command -v gui-agent >/dev/null 2>&1 || [[ -x "${HOME}/.local/bin/gui-agent" ]]; then
        INSTALLED_BINS+=("gui-agent")
    fi
    if command -v mcp-gui-server >/dev/null 2>&1 || [[ -x "${HOME}/.local/bin/mcp-gui-server" ]]; then
        INSTALLED_BINS+=("mcp-gui-server")
    fi
    if command -v gui-agent-atspi >/dev/null 2>&1 || [[ -x "${HOME}/.local/bin/gui-agent-atspi" ]]; then
        INSTALLED_BINS+=("gui-agent-atspi")
    fi

    if [[ ${#INSTALLED_BINS[@]} -gt 0 ]]; then
        log_success "Exécutables installés avec succès dans ~/.local/bin : ${INSTALLED_BINS[*]}"
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
        if [[ "$NON_INTERACTIVE" != "true" && -t 0 ]]; then
            echo -e "${YELLOW}Voulez-vous enregistrer automatiquement gui-agent dans Claude Code CLI ? [O/n]${NC} "
            response=""
            read -r response || response="n"
            if [[ ! "$response" =~ ^([oO][uU][iI]|[oO]|"")$ ]]; then
                CONFIGURE_CLAUDE=false
            fi
        fi

        if [[ "$CONFIGURE_CLAUDE" == "true" ]]; then
            log_info "Enregistrement dans Claude Code : claude mcp add gui-agent -- gui-agent"
            if claude mcp add gui-agent -- gui-agent 2>/dev/null; then
                log_success "Serveur MCP configuré pour Claude Code."
            else
                log_warn "Claude MCP add a retourné un statut non nul (le serveur est peut-être déjà configuré)."
            fi
        fi
    fi

    # 2. Antigravity CLI Integration (~/.gemini/config/mcp_config.json)
    ANTIGRAVITY_CONFIG_DIR="${HOME}/.gemini/config"
    ANTIGRAVITY_CONFIG_FILE="${ANTIGRAVITY_CONFIG_DIR}/mcp_config.json"
    if [[ -d "${HOME}/.gemini" ]]; then
        log_info "Environnement Antigravity CLI détecté."
        mkdir -p "$ANTIGRAVITY_CONFIG_DIR"
        
        # Injection / fusion sécurisée dans mcp_config.json via python
        if "$UV_PATH" run python - <<EOF
import json
import os
import sys
import tempfile

config_path = "$ANTIGRAVITY_CONFIG_FILE"
data = {"mcpServers": {}}

if os.path.exists(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "mcpServers" not in data:
                data["mcpServers"] = {}
            elif not isinstance(data["mcpServers"], dict):
                raise ValueError("Format JSON invalide (mcpServers doit être un dictionnaire ou absent)")
    except Exception as err:
        print(f"Erreur lors de la lecture de {config_path}: {err}", file=sys.stderr)
        sys.exit(1)

data["mcpServers"]["gui-agent"] = {
    "command": "gui-agent",
    "args": [],
    "env": {
        "DISPLAY": os.environ.get("DISPLAY", ":0")
    }
}

config_dir = os.path.dirname(config_path)
tmp_name = None
try:
    with tempfile.NamedTemporaryFile("w", dir=config_dir, delete=False, encoding="utf-8") as tmp_f:
        tmp_name = tmp_f.name
        json.dump(data, tmp_f, indent=2, ensure_ascii=False)
        tmp_f.write("\n")
        tmp_f.flush()
        os.fsync(tmp_f.fileno())
    os.replace(tmp_name, config_path)
except Exception as err:
    if tmp_name and os.path.exists(tmp_name):
        try:
            os.remove(tmp_name)
        except OSError:
            pass
    print(f"Erreur lors de l'écriture atomique de {config_path}: {err}", file=sys.stderr)
    sys.exit(1)
EOF
        then
            log_success "Configuration Antigravity CLI mise à jour dans $ANTIGRAVITY_CONFIG_FILE"
        else
            log_warn "Impossible de mettre à jour la configuration Antigravity CLI dans $ANTIGRAVITY_CONFIG_FILE"
        fi
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
