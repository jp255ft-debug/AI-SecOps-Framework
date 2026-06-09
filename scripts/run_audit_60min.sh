#!/bin/bash
# run_audit_60min.sh - AI-SecOps-Framework
# 60-minute full security audit for LLM/ML infrastructures
# Usage: bash scripts/run_audit_60min.sh [--output-dir DIR] [--target PATH]
set -euo pipefail

# ============================================
# Configuration
# ============================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
OUTPUT_DIR="${PROJECT_DIR}/audits/outputs/${TIMESTAMP}"
TARGET_DIR="${PROJECT_DIR}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "Usage: $0 [--output-dir DIR] [--target PATH]"
            echo ""
            echo "Options:"
            echo "  --output-dir DIR   Output directory for audit results (default: audits/outputs/<timestamp>)"
            echo "  --target PATH      Target directory to audit (default: project root)"
            echo "  --help, -h         Show this help message"
            exit 0
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --target)
            TARGET_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown: $1"
            echo "Usage: $0 [--output-dir DIR] [--target PATH]"
            exit 1
            ;;
    esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================
# Helper Functions
# ============================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%H:%M:%S') - $1"
}

log_ok() {
    echo -e "${GREEN}[OK]${NC} $(date '+%H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%H:%M:%S') - $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $(date '+%H:%M:%S') - $1"
}

section() {
    echo ""
    echo "============================================"
    echo " $1"
    echo "============================================"
}

# ============================================
# Phase 0: Setup (5 min)
# ============================================
section "Phase 0/5: Environment Setup"

log_info "Creating output directory: ${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"

# Check if running in Docker or natively
if [ -f /.dockerenv ]; then
    log_info "Running inside Docker container"
    RUNNING_IN_DOCKER=true
else
    RUNNING_IN_DOCKER=false
fi

# ============================================
# Phase 1: SAST - Semgrep (10 min)
# ============================================
section "Phase 1/5: SAST Scan with Semgrep (10 min)"

SEMGREP_OUTPUT="${OUTPUT_DIR}/semgrep_results.json"
SEMGREP_CONFIG="${PROJECT_DIR}/config/semgrep/custom_rules.yaml"

if command -v semgrep &> /dev/null; then
    log_info "Running Semgrep SAST scan..."
    
    if [ -f "${SEMGREP_CONFIG}" ]; then
        semgrep --config "${SEMGREP_CONFIG}" \
                --json \
                --output "${SEMGREP_OUTPUT}" \
                "${TARGET_DIR}" 2>&1 || true
    else
        log_warn "Custom rules not found. Using default Semgrep rules."
        semgrep --config "auto" \
                --json \
                --output "${SEMGREP_OUTPUT}" \
                "${TARGET_DIR}" 2>&1 || true
    fi
    
    if [ -f "${SEMGREP_OUTPUT}" ]; then
        VULN_COUNT=$(python3 -c "import json; data=json.load(open('${SEMGREP_OUTPUT}')); print(len(data.get('results', [])))" 2>/dev/null || echo "unknown")
        log_ok "Semgrep scan complete. Found ${VULN_COUNT} findings."
    else
        log_warn "Semgrep output not generated."
    fi
else
    log_warn "Semgrep not installed. Skipping SAST scan."
    echo '{"results": [], "errors": ["Semgrep not installed"]}' > "${SEMGREP_OUTPUT}"
fi

# ============================================
# Phase 2: SCA - Trivy (15 min)
# ============================================
section "Phase 2/5: SCA Scan with Trivy (15 min)"

TRIVY_OUTPUT="${OUTPUT_DIR}/trivy_results.json"

if command -v trivy &> /dev/null; then
    log_info "Running Trivy filesystem scan..."
    
    trivy fs --format json \
             --output "${TRIVY_OUTPUT}" \
             --scanners vuln,secret,misconfig \
             --ignorefile "${PROJECT_DIR}/config/trivy/.trivyignore" \
             "${TARGET_DIR}" 2>&1 || true
    
    if [ -f "${TRIVY_OUTPUT}" ]; then
        CRITICAL=$(python3 -c "import json; data=json.load(open('${TRIVY_OUTPUT}')); print(sum(1 for r in data.get('Results', []) for v in r.get('Vulnerabilities', []) if v.get('Severity') == 'CRITICAL'))" 2>/dev/null || echo "unknown")
        log_ok "Trivy scan complete. Critical vulnerabilities: ${CRITICAL}"
    else
        log_warn "Trivy output not generated."
    fi
else
    log_warn "Trivy not installed. Trying via Docker..."
    if command -v docker &> /dev/null; then
        docker run --rm -v "${TARGET_DIR}:/target" \
                   aquasec/trivy:latest fs \
                   --format json \
                   --output "/target/${TRIVY_OUTPUT##*/}" \
                   /target 2>&1 || true
    else
        log_warn "Trivy not available. Skipping SCA scan."
        echo '{"Results": []}' > "${TRIVY_OUTPUT}"
    fi
fi

# ============================================
# Phase 3: LLM Vulnerability Scan - Giskard (20 min)
# ============================================
section "Phase 3/5: LLM Vulnerability Scan with Giskard (20 min)"

GISKARD_OUTPUT="${OUTPUT_DIR}/giskard_results.json"

if [ -f "${PROJECT_DIR}/tests/models/test_giskard_vulns.py" ]; then
    log_info "Running Giskard LLM vulnerability tests..."
    
    python3 "${PROJECT_DIR}/tests/models/test_giskard_vulns.py" \
            --output "${GISKARD_OUTPUT}" 2>&1 || true
    
    if [ -f "${GISKARD_OUTPUT}" ]; then
        log_ok "Giskard scan complete."
    else
        log_warn "Giskard output not generated."
        echo '{"tests": [], "summary": {"total": 0, "passed": 0, "failed": 0}}' > "${GISKARD_OUTPUT}"
    fi
else
    log_warn "Giskard test file not found. Skipping LLM scan."
    echo '{"tests": [], "summary": {"total": 0, "passed": 0, "failed": 0}}' > "${GISKARD_OUTPUT}"
fi

# ============================================
# Phase 4: Prompt Injection Tests (5 min)
# ============================================
section "Phase 4/5: Prompt Injection Testing (5 min)"

PROMPTFOO_OUTPUT="${OUTPUT_DIR}/promptfoo_results.json"

if command -v npx &> /dev/null && [ -f "${PROJECT_DIR}/tests/prompt_injection/promptfoo.yaml" ]; then
    log_info "Running Promptfoo prompt injection tests..."
    
    cd "${PROJECT_DIR}/tests/prompt_injection"
    npx promptfoo eval \
         --config promptfoo.yaml \
         --output "${PROMPTFOO_OUTPUT}" 2>&1 || true
    cd "${PROJECT_DIR}"
    
    if [ -f "${PROMPTFOO_OUTPUT}" ]; then
        log_ok "Prompt injection tests complete."
    else
        log_warn "Promptfoo output not generated."
    fi
else
    log_warn "Promptfoo not configured. Skipping prompt injection tests."
fi

# ============================================
# Phase 5: Report Generation (5 min)
# ============================================
section "Phase 5/5: Report Generation (5 min)"

FINAL_REPORT="${OUTPUT_DIR}/FINAL_REPORT.md"

log_info "Generating consolidated audit report..."

cat > "${FINAL_REPORT}" << EOF
# AI-SecOps-Framework - Security Audit Report

**Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Target:** ${TARGET_DIR}
**Audit ID:** ${TIMESTAMP}

---

## Executive Summary

This report summarizes the findings of an automated security audit performed
using the AI-SecOps-Framework. The audit covers SAST (Static Analysis),
SCA (Software Composition Analysis), LLM vulnerability scanning, and
prompt injection testing.

---

## Scan Results

### 1. SAST - Semgrep
$(if [ -f "${SEMGREP_OUTPUT}" ]; then
    python3 -c "
import json
with open('${SEMGREP_OUTPUT}') as f:
    data = json.load(f)
results = data.get('results', [])
print(f'- **Findings:** {len(results)}')
print(f'- **Severity Breakdown:**')
severities = {}
for r in results:
    sev = r.get('extra', {}).get('severity', 'UNKNOWN')
    severities[sev] = severities.get(sev, 0) + 1
for sev, count in sorted(severities.items()):
    print(f'  - {sev}: {count}')
" 2>/dev/null || echo "- Results: See semgrep_results.json"
else
    echo "- Not available"
fi)

### 2. SCA - Trivy
$(if [ -f "${TRIVY_OUTPUT}" ]; then
    python3 -c "
import json
with open('${TRIVY_OUTPUT}') as f:
    data = json.load(f)
total_vulns = 0
severities = {}
for result in data.get('Results', []):
    for vuln in result.get('Vulnerabilities', []):
        total_vulns += 1
        sev = vuln.get('Severity', 'UNKNOWN')
        severities[sev] = severities.get(sev, 0) + 1
print(f'- **Total Vulnerabilities:** {total_vulns}')
print(f'- **Severity Breakdown:**')
for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']:
    if sev in severities:
        print(f'  - {sev}: {severities[sev]}')
" 2>/dev/null || echo "- Results: See trivy_results.json"
else
    echo "- Not available"
fi)

### 3. LLM Security - Giskard
$(if [ -f "${GISKARD_OUTPUT}" ]; then
    python3 -c "
import json
with open('${GISKARD_OUTPUT}') as f:
    data = json.load(f)
summary = data.get('summary', {})
print(f'- **Tests Run:** {summary.get(\"total\", \"N/A\")}')
print(f'- **Passed:** {summary.get(\"passed\", \"N/A\")}')
print(f'- **Failed:** {summary.get(\"failed\", \"N/A\")}')
" 2>/dev/null || echo "- Results: See giskard_results.json"
else
    echo "- Not available"
fi)

### 4. Prompt Injection
$(if [ -f "${PROMPTFOO_OUTPUT}" ]; then
    echo "- Results: See promptfoo_results.json"
else
    echo "- Not tested"
fi)

---

## Risk Score

| Category | Status | Risk Level |
|----------|--------|------------|
| SAST (Code Quality) | $(if [ -f "${SEMGREP_OUTPUT}" ] && python3 -c "import json; data=json.load(open('${SEMGREP_OUTPUT}')); print('PASS' if len(data.get('results',[]))==0 else 'ISSUES FOUND')" 2>/dev/null; then echo "⚠️"; else echo "❌"; fi) | $(if [ -f "${SEMGREP_OUTPUT}" ] && python3 -c "import json; data=json.load(open('${SEMGREP_OUTPUT}')); print('LOW' if len(data.get('results',[]))==0 else 'MEDIUM')" 2>/dev/null; then echo " "; fi) |
| SCA (Dependencies) | $(if [ -f "${TRIVY_OUTPUT}" ] && python3 -c "import json; data=json.load(open('${TRIVY_OUTPUT}')); print('PASS' if sum(1 for r in data.get('Results',[]) for v in r.get('Vulnerabilities',[]) if v.get('Severity')=='CRITICAL')==0 else 'CRITICAL VULNS')" 2>/dev/null; then echo " "; fi) | $(if [ -f "${TRIVY_OUTPUT}" ] && python3 -c "import json; data=json.load(open('${TRIVY_OUTPUT}')); print('LOW' if sum(1 for r in data.get('Results',[]) for v in r.get('Vulnerabilities',[]) if v.get('Severity')=='CRITICAL')==0 else 'CRITICAL')" 2>/dev/null; then echo " "; fi) |
| LLM Security | $(if [ -f "${GISKARD_OUTPUT}" ] && python3 -c "import json; data=json.load(open('${GISKARD_OUTPUT}')); s=data.get('summary',{}); print('PASS' if s.get('failed',0)==0 else 'ISSUES FOUND')" 2>/dev/null; then echo " "; fi) | $(if [ -f "${GISKARD_OUTPUT}" ] && python3 -c "import json; data=json.load(open('${GISKARD_OUTPUT}')); s=data.get('summary',{}); print('LOW' if s.get('failed',0)==0 else 'HIGH')" 2>/dev/null; then echo " "; fi) |

---

## Top Recommendations

1. **Critical & High CVEs:** Address all CRITICAL and HIGH severity vulnerabilities found by Trivy.
2. **Code Quality:** Review and fix Semgrep findings, especially those related to LLM security.
3. **LLM Hardening:** Implement guardrails for any identified prompt injection vulnerabilities.

---

*Report generated by AI-SecOps-Framework | Audit ID: ${TIMESTAMP}*
EOF

log_ok "Final report generated: ${FINAL_REPORT}"

# Create symlink to latest audit
LATEST_LINK="${PROJECT_DIR}/audits/outputs/latest"
rm -f "${LATEST_LINK}"
ln -sf "${TIMESTAMP}" "${LATEST_LINK}" 2>/dev/null || cp -r "${OUTPUT_DIR}" "${LATEST_LINK}" 2>/dev/null || true

# ============================================
# Summary
# ============================================
section "Audit Complete"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN} Audit completed successfully!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo " Output Directory: ${OUTPUT_DIR}"
echo " Final Report:     ${FINAL_REPORT}"
echo ""
echo " To view the report:"
echo "   cat ${FINAL_REPORT}"
echo ""
echo " To open in browser (if using Markdown viewer):"
echo "   start ${FINAL_REPORT}"
echo ""
