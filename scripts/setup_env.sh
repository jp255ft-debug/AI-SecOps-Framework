#!/bin/bash
# setup_env.sh - AI-SecOps-Framework
# Environment setup and dependency installer
# Usage: bash scripts/setup_env.sh
set -euo pipefail

echo "============================================"
echo " AI-SecOps-Framework - Environment Setup"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
check_version() {
    local cmd=$1
    local min_version=$2
    local name=$3
    
    if ! command -v "$cmd" &> /dev/null; then
        echo -e "${RED}[FAIL]${NC} $name is not installed. Please install $name >= $min_version"
        return 1
    fi
    
    local version
    version=$("$cmd" --version 2>&1 | head -n1 | grep -oP '\d+\.\d+\.\d+' | head -n1)
    
    if [ -z "$version" ]; then
        echo -e "${YELLOW}[WARN]${NC} Could not determine $name version. Assuming installed."
        return 0
    fi
    
    # Compare versions (simple string comparison - works for major.minor.patch)
    if [ "$(printf '%s\n' "$min_version" "$version" | sort -V | head -n1)" = "$version" ] && [ "$version" != "$min_version" ]; then
        echo -e "${RED}[FAIL]${NC} $name version $version is too old. Minimum required: $min_version"
        return 1
    fi
    
    echo -e "${GREEN}[OK]${NC} $name version $version"
    return 0
}

echo ""
echo "--- Step 1: Checking System Dependencies ---"

# Check required tools
check_version "python3" "3.10.0" "Python 3" || PYTHON_FAIL=1
check_version "pip3" "21.0.0" "pip" || PIP_FAIL=1
check_version "docker" "20.10.0" "Docker" || DOCKER_FAIL=1
check_version "git" "2.30.0" "Git" || GIT_FAIL=1

# Optional tools (not required for basic audit)
check_version "trivy" "0.50.0" "Trivy" || echo -e "${YELLOW}[INFO]${NC} Trivy will be run via Docker"
check_version "semgrep" "1.60.0" "Semgrep" || echo -e "${YELLOW}[INFO]${NC} Semgrep will be installed via pip"

echo ""
echo "--- Step 2: Installing Python Dependencies ---"

if [ -f "requirements.txt" ]; then
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    echo -e "${GREEN}[OK]${NC} Python dependencies installed"
else
    echo -e "${RED}[FAIL]${NC} requirements.txt not found"
    exit 1
fi

echo ""
echo "--- Step 3: Setting Up Git Hooks ---"

if [ -d ".githooks" ]; then
    git config core.hooksPath .githooks
    echo -e "${GREEN}[OK]${NC} Git hooks configured"
fi

echo ""
echo "--- Step 4: Creating Output Directories ---"

mkdir -p audits/outputs
echo -e "${GREEN}[OK]${NC} Output directories created"

echo ""
echo "============================================"
echo -e "${GREEN} Setup Complete!${NC}"
echo " Run 'make audit' to start a security audit"
echo "============================================"
