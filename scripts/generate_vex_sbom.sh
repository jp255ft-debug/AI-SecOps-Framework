#!/bin/bash
# generate_vex_sbom.sh - AI-SecOps-Framework
# Generate SBOM (CycloneDX + SPDX) and VEX documents
# Usage: bash scripts/generate_vex_sbom.sh [--output-dir DIR]
set -euo pipefail

# ============================================
# Configuration
# ============================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
OUTPUT_DIR="${PROJECT_DIR}/audits/outputs/${TIMESTAMP}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--output-dir DIR]"
            exit 1
            ;;
    esac
done

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $(date '+%H:%M:%S') - $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $(date '+%H:%M:%S') - $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $(date '+%H:%M:%S') - $1"; }

# ============================================
# Main
# ============================================
mkdir -p "${OUTPUT_DIR}"
log_info "Output directory: ${OUTPUT_DIR}"

# Generate CycloneDX SBOM
log_info "Generating CycloneDX SBOM..."
if command -v cyclonedx-py &> /dev/null; then
    cyclonedx-py requirements \
        --output "${OUTPUT_DIR}/sbom.cyclonedx.json" \
        --format json
    log_info "CycloneDX SBOM generated: sbom.cyclonedx.json"
else
    log_warn "cyclonedx-py not installed. Installing..."
    pip install cyclonedx-bom
    cyclonedx-py requirements \
        --output "${OUTPUT_DIR}/sbom.cyclonedx.json" \
        --format json
    log_info "CycloneDX SBOM generated: sbom.cyclonedx.json"
fi

# Generate SPDX SBOM
log_info "Generating SPDX SBOM..."
if python -c "import spdx_tools" 2>/dev/null; then
    python -m spdx_tools.generate \
        "${PROJECT_DIR}/requirements.txt" \
        --output "${OUTPUT_DIR}/sbom.spdx.json"
    log_info "SPDX SBOM generated: sbom.spdx.json"
else
    log_warn "spdx-tools not installed. Installing..."
    pip install spdx-tools
    python -m spdx_tools.generate \
        "${PROJECT_DIR}/requirements.txt" \
        --output "${OUTPUT_DIR}/sbom.spdx.json"
    log_info "SPDX SBOM generated: sbom.spdx.json"
fi

# Generate VEX document (placeholder for known vulnerabilities)
log_info "Generating VEX document..."
cat > "${OUTPUT_DIR}/vex.json" << VEXEOF
{
  "@context": "https://openvex.dev/ns/v0.2.0",
  "@id": "https://github.com/jp255ft-debug/AI-SecOps-Framework/vex/${TIMESTAMP}",
  "author": "AI-SecOps-Framework",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "version": 1,
  "statements": []
}
VEXEOF
log_info "VEX document generated: vex.json"

# Summary
echo ""
echo "============================================"
echo " SBOM Generation Complete"
echo "============================================"
echo ""
echo " Output: ${OUTPUT_DIR}"
echo ""
echo " Files:"
ls -la "${OUTPUT_DIR}/"
echo ""
echo " To verify SBOM:"
echo "   cat ${OUTPUT_DIR}/sbom.cyclonedx.json | python -m json.tool"
echo ""
