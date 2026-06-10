#!/bin/bash
# setup_tools.sh - AI-SecOps-Framework
# Instala ferramentas externas necessárias para o pipeline completo
# Usage: bash scripts/setup_tools.sh
set -euo pipefail

# ============================================
# Configuration
# ============================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_fail()  { echo -e "${RED}[FAIL]${NC} $1"; }

section() {
    echo ""
    echo "============================================"
    echo " $1"
    echo "============================================"
}

# ============================================
# Detect OS
# ============================================
if grep -qi microsoft /proc/version 2>/dev/null; then
    IS_WSL=true
    log_info "Detected WSL environment"
else
    IS_WSL=false
    log_info "Detected native Linux environment"
fi

# ============================================
# 1. Install zstd (required for Ollama)
# ============================================
section "1/4: Installing zstd"

if command -v zstd &> /dev/null; then
    log_ok "zstd already installed ($(zstd --version))"
else
    log_info "Installing zstd..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y -qq zstd
        log_ok "zstd installed successfully"
    elif command -v brew &> /dev/null; then
        brew install zstd
        log_ok "zstd installed successfully"
    else
        log_warn "Could not install zstd. Please install manually: sudo apt install zstd"
    fi
fi

# ============================================
# 2. Install Ollama
# ============================================
section "2/4: Installing Ollama"

if command -v ollama &> /dev/null; then
    log_ok "Ollama already installed ($(ollama --version 2>/dev/null || echo 'version unknown'))"
else
    log_info "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    log_ok "Ollama installed successfully"
    log_info "Pull a model: ollama pull llama3.2"
fi

# ============================================
# 3. Install Promptfoo
# ============================================
section "3/4: Installing Promptfoo"

if command -v promptfoo &> /dev/null; then
    log_ok "Promptfoo already installed ($(promptfoo --version 2>/dev/null || echo 'version unknown'))"
elif command -v npx &> /dev/null; then
    log_info "Promptfoo not found globally. Installing via npm..."
    if [ "$IS_WSL" = true ]; then
        # WSL: install locally to avoid permission issues
        npm install -g promptfoo 2>&1 || {
            log_warn "Global install failed. Trying local install..."
            cd "$PROJECT_DIR"
            npm install promptfoo --save-dev 2>&1 || true
        }
    else
        sudo npm install -g promptfoo
    fi
    
    if command -v promptfoo &> /dev/null; then
        log_ok "Promptfoo installed successfully"
    else
        log_warn "Promptfoo not in PATH. Use 'npx promptfoo' instead."
    fi
else
    log_warn "npm not found. Install Node.js first: https://nodejs.org/"
fi

# ============================================
# 4. Verify Docker (WSL integration check)
# ============================================
section "4/4: Verifying Docker"

if command -v docker &> /dev/null; then
    log_ok "Docker found ($(docker --version))"
    if docker info &>/dev/null; then
        log_ok "Docker daemon is running"
    else
        log_warn "Docker daemon is not running."
        if [ "$IS_WSL" = true ]; then
            echo "   → Start Docker Desktop on Windows and enable WSL integration."
            echo "   → Then run: wsl --shutdown && wsl"
        else
            echo "   → Start Docker: sudo systemctl start docker"
        fi
    fi
else
    log_warn "Docker not found."
    if [ "$IS_WSL" = true ]; then
        echo "   → Install Docker Desktop on Windows and enable WSL integration."
    else
        echo "   → Install Docker: curl -fsSL https://get.docker.com | sh"
    fi
fi

# ============================================
# Summary
# ============================================
section "Setup Complete"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN} Tool setup completed!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo " Next steps:"
echo "   1. Pull an Ollama model:  ollama pull llama3.2"
echo "   2. Run prompt tests:      cd tests/prompt_injection && npx promptfoo eval"
echo "   3. Run full audit:        bash scripts/run_audit_60min.sh --target https://github.com/user/repo.git"
echo "   4. Start observability:   docker compose -f docker-compose.otel.yml up -d"
echo ""
