#!/usr/bin/env bash
# ==============================================================================
# FastMCP GUI Agent - Local Continuous Integration (CI) Runner
# Mirrors the Python workflow defined in .github/workflows/ci.yml
# ==============================================================================

set -uo pipefail

# ANSI Colors
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Help flag
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo -e "${BOLD}FastMCP GUI Agent - Script CI Local${NC}"
    echo "Usage: ./ci.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help       Affiche cette aide et quitte."
    echo "  --quick          Exécute la compilation, la validation des workflows, le linter et les tests (ignore mypy et le formatage)."
    echo "  --no-headless    Désactive l'exécution sous xvfb-run pour les tests."
    exit 0
fi

QUICK_MODE=0
USE_XVFB=1

for arg in "$@"; do
    case "$arg" in
        --quick)
            QUICK_MODE=1
            ;;
        --no-headless)
            USE_XVFB=0
            ;;
    esac
done

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${CYAN}🚀 FAST-MCP GUI AGENT : Exécution de la CI Locale${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 1. Détection de l'environnement Python & des outils
PYTHON_BIN=""
UV_BIN=$(command -v uv 2>/dev/null || echo "${HOME}/.local/bin/uv")

if [ -f "./venv/bin/python" ]; then
    PYTHON_BIN="./venv/bin/python"
elif [ -f "./.venv/bin/python" ]; then
    PYTHON_BIN="./.venv/bin/python"
elif command -v "$UV_BIN" >/dev/null 2>&1; then
    PYTHON_BIN="$UV_BIN run python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo -e "${RED}❌ Aucun interpréteur Python trouvé (venv, uv ou python3 requis).${NC}"
    exit 1
fi

echo -e "${BLUE}ℹ Interpréteur Python :${NC} $PYTHON_BIN"

# Détection de Ruff
RUFF_CMD=""
if [ -f "./venv/bin/ruff" ]; then
    RUFF_CMD="./venv/bin/ruff"
elif [ -f "./.venv/bin/ruff" ]; then
    RUFF_CMD="./.venv/bin/ruff"
elif command -v ruff >/dev/null 2>&1; then
    RUFF_CMD="ruff"
elif command -v "$UV_BIN" >/dev/null 2>&1; then
    RUFF_CMD="$UV_BIN run --with ruff ruff"
else
    RUFF_CMD="$PYTHON_BIN -m ruff"
fi

# Détection de Mypy
MYPY_CMD=""
if [ -f "./venv/bin/mypy" ]; then
    MYPY_CMD="./venv/bin/mypy"
elif [ -f "./.venv/bin/mypy" ]; then
    MYPY_CMD="./.venv/bin/mypy"
elif command -v mypy >/dev/null 2>&1; then
    MYPY_CMD="mypy"
elif command -v "$UV_BIN" >/dev/null 2>&1; then
    MYPY_CMD="$UV_BIN run --with mypy mypy"
else
    MYPY_CMD="$PYTHON_BIN -m mypy"
fi

# Détection de Pytest
PYTEST_CMD=""
if [ -f "./venv/bin/pytest" ]; then
    PYTEST_CMD="./venv/bin/pytest"
elif [ -f "./.venv/bin/pytest" ]; then
    PYTEST_CMD="./.venv/bin/pytest"
elif command -v pytest >/dev/null 2>&1; then
    PYTEST_CMD="pytest"
elif command -v "$UV_BIN" >/dev/null 2>&1; then
    PYTEST_CMD="$UV_BIN run --with pytest pytest"
else
    PYTEST_CMD="$PYTHON_BIN -m pytest"
fi

# Configuration XVFB pour tests headless si disponible
if [ "$USE_XVFB" -eq 1 ] && command -v xvfb-run >/dev/null 2>&1; then
    TEST_RUNNER="xvfb-run -a $PYTEST_CMD"
    echo -e "${BLUE}ℹ Serveur graphique virtuel :${NC} xvfb-run actif"
else
    TEST_RUNNER="$PYTEST_CMD"
    echo -e "${BLUE}ℹ Serveur graphique virtuel :${NC} direct (DISPLAY=${DISPLAY:-non-défini})"
fi
echo ""

# Tableau des résultats
declare -a STEP_NAMES=()
declare -a STEP_STATUS=()
declare -a STEP_DURATIONS=()
GLOBAL_SUCCESS=1

run_step() {
    local name="$1"
    local cmd="$2"
    
    echo -e "${BOLD}▶ [Étape $(( ${#STEP_NAMES[@]} + 1 ))] ${name}...${NC}"
    local start_time
    start_time=$(date +%s%N 2>/dev/null || date +%s)
    
    if eval "$cmd"; then
        local end_time
        end_time=$(date +%s%N 2>/dev/null || date +%s)
        local duration_ms=0
        if [ "$start_time" -gt 1000000000000 2>/dev/null ]; then
            duration_ms=$(( (end_time - start_time) / 1000000 ))
        else
            duration_ms=$(( (end_time - start_time) * 1000 ))
        fi
        
        STEP_NAMES+=("$name")
        STEP_STATUS+=("PASS")
        STEP_DURATIONS+=("${duration_ms}ms")
        echo -e "${GREEN}✔ Validé (${duration_ms}ms)${NC}\n"
    else
        local end_time
        end_time=$(date +%s%N 2>/dev/null || date +%s)
        local duration_ms=0
        if [ "$start_time" -gt 1000000000000 2>/dev/null ]; then
            duration_ms=$(( (end_time - start_time) / 1000000 ))
        else
            duration_ms=$(( (end_time - start_time) * 1000 ))
        fi
        
        STEP_NAMES+=("$name")
        STEP_STATUS+=("FAIL")
        STEP_DURATIONS+=("${duration_ms}ms")
        GLOBAL_SUCCESS=0
        echo -e "${RED}✖ Échec de l'étape ($name)${NC}\n"
    fi
}

# 1. Compilation Bytecode Python
run_step "Compilation Bytecode Python (compileall)" "$PYTHON_BIN -m compileall -q -x '(\.venv|venv|\.git|\.GCC|screenshots|dist|build)' ."

# 2. Vérification de la Logique et Sécurité des Workflows GitHub Actions
run_step "Validation Workflows GitHub Actions" "$PYTHON_BIN .github/scripts/verify_workflows.py .github/workflows"

# 3. Linter Ruff
run_step "Linter de Code (Ruff Check)" "$RUFF_CMD check ."

if [ "$QUICK_MODE" -eq 0 ]; then
    # 4. Formatage de Code
    run_step "Formatage de Code (Ruff Format)" "$RUFF_CMD format --check ."

    # 5. Typage Statique
    run_step "Typage Statique Strict (Mypy)" "$MYPY_CMD gui_agent mcp_gui_server.py"
fi

# 6. Tests Pytest
run_step "Suite de Tests Pytest" "$TEST_RUNNER -v tests/"

# Affichage du tableau récapitulatif
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${CYAN}📊 RÉSUMÉ D'EXÉCUTION CI (CI Summary)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
printf "| %-42s | %-10s | %-10s |\n" "Étape de Validation" "Statut" "Durée"
printf "|-%-42s-|-%-10s-|-%-10s-|\n" "------------------------------------------" "----------" "----------"

for i in "${!STEP_NAMES[@]}"; do
    local_stat="${STEP_STATUS[$i]}"
    if [ "$local_stat" == "PASS" ]; then
        local_badge="${GREEN}PASS${NC}"
    else
        local_badge="${RED}FAIL${NC}"
    fi
    printf "| %-42s | %-19b | %-10s |\n" "${STEP_NAMES[$i]}" "$local_badge" "${STEP_DURATIONS[$i]}"
done
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ "$GLOBAL_SUCCESS" -eq 1 ]; then
    echo -e "${GREEN}${BOLD}🎉 Toutes les étapes CI sont validées avec succès !${NC}"
    exit 0
else
    echo -e "${RED}${BOLD}❌ Échec de la CI locale : Corrigez les erreurs ci-dessus.${NC}"
    exit 1
fi
