#!/usr/bin/env python3
"""
Threat Model Generator for AI-SecOps-Framework.
Uses STRIDE methodology adapted for LLM/ML systems.

Usage:
    python scripts/generate_threat_model.py

Output:
    - docs/architecture/threat-model.md (Markdown report)
    - docs/architecture/threat-model.json (JSON for tooling)
"""
import json
import os
from dataclasses import dataclass, asdict
from typing import List
from datetime import datetime


@dataclass
class Threat:
    """A single threat in the STRIDE model."""
    id: str
    category: str  # STRIDE: Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation
    description: str
    affected_component: str
    severity: str  # Critical, High, Medium, Low
    likelihood: str  # High, Medium, Low
    mitigation: str
    owasp_llm: str  # LLM01-LLM10
    status: str  # Mitigated, Partial, Not Addressed


class ThreatModelGenerator:
    """Generate STRIDE threat model for AI-SecOps-Framework."""
    
    def __init__(self):
        self.threats: List[Threat] = []
        self._define_threats()
    
    def _define_threats(self):
        """Define known threats to the system."""
        
        # ============================================
        # Spoofing
        # ============================================
        self.threats.append(Threat(
            id="T001",
            category="Spoofing",
            description="Attacker spoofs LLM API responses to inject malicious content into the application",
            affected_component="LLM API Client (openai, anthropic)",
            severity="High",
            likelihood="Low",
            mitigation="Use TLS pinning, verify API certificates, implement response validation with NeMo Guardrails",
            owasp_llm="LLM02",
            status="Partial"
        ))
        
        # ============================================
        # Tampering
        # ============================================
        self.threats.append(Threat(
            id="T002",
            category="Tampering",
            description="Attacker tampers with audit reports in storage to hide vulnerabilities",
            affected_component="audits/outputs/",
            severity="Medium",
            likelihood="Low",
            mitigation="Generate cryptographic signatures (HMAC-SHA256) for reports, use git for audit trail",
            owasp_llm="N/A",
            status="Not Addressed"
        ))
        
        self.threats.append(Threat(
            id="T003",
            category="Tampering",
            description="Attacker modifies Semgrep rules to suppress vulnerability detection",
            affected_component="config/semgrep/custom_rules.yaml",
            severity="High",
            likelihood="Low",
            mitigation="Code review on rule changes, sign rules with GPG, CI validation of rule integrity",
            owasp_llm="N/A",
            status="Not Addressed"
        ))
        
        # ============================================
        # Repudiation
        # ============================================
        self.threats.append(Threat(
            id="T004",
            category="Repudiation",
            description="User denies running malicious audit command or accessing sensitive results",
            affected_component="CLI (guardrails/cli.py)",
            severity="Low",
            likelihood="Low",
            mitigation="Implement audit logging to syslog/CloudWatch, log all CLI invocations with user identity",
            owasp_llm="N/A",
            status="Not Addressed"
        ))
        
        # ============================================
        # Information Disclosure
        # ============================================
        self.threats.append(Threat(
            id="T005",
            category="Information Disclosure",
            description="Prompt injection causes LLM to leak training data, system prompts, or sensitive business logic",
            affected_component="LLM API Calls",
            severity="Critical",
            likelihood="High",
            mitigation="NeMo Guardrails input validation, Semgrep rules for prompt injection (LLM01), output sanitization",
            owasp_llm="LLM01",
            status="Mitigated"
        ))
        
        self.threats.append(Threat(
            id="T006",
            category="Information Disclosure",
            description="Secrets (API keys, tokens) leaked in audit reports or logs",
            affected_component="audits/outputs/*.md, logs",
            severity="Critical",
            likelihood="Medium",
            mitigation="Gitleaks scanning in CI, output sanitization in report generator, .gitignore for outputs/",
            owasp_llm="LLM06",
            status="Mitigated"
        ))
        
        self.threats.append(Threat(
            id="T007",
            category="Information Disclosure",
            description="Sensitive data included in LLM prompts sent to external API providers",
            affected_component="LLM API Client",
            severity="Critical",
            likelihood="Medium",
            mitigation="Semgrep rule llm-sensitive-data-in-prompt (LLM06), input sanitization, data classification",
            owasp_llm="LLM06",
            status="Mitigated"
        ))
        
        # ============================================
        # Denial of Service
        # ============================================
        self.threats.append(Threat(
            id="T008",
            category="Denial of Service",
            description="Unbounded input causes LLM API cost explosion or resource exhaustion",
            affected_component="LLM API Client",
            severity="High",
            likelihood="Medium",
            mitigation="Input length limits (4096 chars), rate limiting, cost monitoring, Semgrep rule llm-dos-unbounded-input",
            owasp_llm="LLM04",
            status="Partial"
        ))
        
        self.threats.append(Threat(
            id="T009",
            category="Denial of Service",
            description="Malicious payload causes Semgrep or Trivy to crash during audit",
            affected_component="scripts/run_audit_60min.sh",
            severity="Medium",
            likelihood="Low",
            mitigation="Timeouts on all tool executions, graceful error handling, resource limits in Docker",
            owasp_llm="N/A",
            status="Partial"
        ))
        
        # ============================================
        # Elevation of Privilege
        # ============================================
        self.threats.append(Threat(
            id="T010",
            category="Elevation of Privilege",
            description="LLM agent executes privileged commands (shell, filesystem) without authorization",
            affected_component="LLM Tool Functions (@tool decorators)",
            severity="Critical",
            likelihood="High",
            mitigation="Semgrep rules for @tool validation (LLM07), require human-in-the-loop (LLM08), sandbox execution",
            owasp_llm="LLM07, LLM08",
            status="Mitigated"
        ))
        
        self.threats.append(Threat(
            id="T011",
            category="Elevation of Privilege",
            description="LLM endpoint exposed without authentication allows model theft",
            affected_component="LLM API Endpoints",
            severity="High",
            likelihood="Medium",
            mitigation="Semgrep rule llm-model-theft-exposed-endpoint (LLM10), API key authentication, rate limiting",
            owasp_llm="LLM10",
            status="Mitigated"
        ))
        
        self.threats.append(Threat(
            id="T012",
            category="Elevation of Privilege",
            description="Dependency confusion attack installs malicious package during pip install",
            affected_component="requirements.txt, pyproject.toml",
            severity="High",
            likelihood="Medium",
            mitigation="Pin dependency versions, use --require-hashes, Dependabot alerts, Trivy scanning",
            owasp_llm="LLM05",
            status="Mitigated"
        ))
    
    def generate_markdown(self) -> str:
        """Generate Markdown threat model report."""
        report = f"""# Threat Model - AI-SecOps-Framework

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Methodology:** STRIDE (adapted for LLM/ML systems)
**Total Threats:** {len(self.threats)}

---

## Executive Summary

| Category | Count | ✅ Mitigated | ⚠️ Partial | ❌ Not Addressed |
|----------|-------|-------------|------------|------------------|
"""
        
        categories = [
            "Spoofing", "Tampering", "Repudiation",
            "Information Disclosure", "Denial of Service",
            "Elevation of Privilege"
        ]
        
        for cat in categories:
            threats = [t for t in self.threats if t.category == cat]
            mitigated = sum(1 for t in threats if t.status == "Mitigated")
            partial = sum(1 for t in threats if t.status == "Partial")
            not_addressed = sum(1 for t in threats if t.status == "Not Addressed")
            report += f"| {cat} | {len(threats)} | {mitigated} | {partial} | {not_addressed} |\n"
        
        # Summary row
        total_mitigated = sum(1 for t in self.threats if t.status == "Mitigated")
        total_partial = sum(1 for t in self.threats if t.status == "Partial")
        total_not = sum(1 for t in self.threats if t.status == "Not Addressed")
        report += f"| **Total** | **{len(self.threats)}** | **{total_mitigated}** | **{total_partial}** | **{total_not}** |\n"
        
        report += "\n### Risk Distribution\n\n"
        severity_counts = {}
        for t in self.threats:
            severity_counts[t.severity] = severity_counts.get(t.severity, 0) + 1
        
        for sev in ["Critical", "High", "Medium", "Low"]:
            count = severity_counts.get(sev, 0)
            bar = "█" * count + "░" * (5 - count)
            report += f"- **{sev}**: {bar} ({count})\n"
        
        report += "\n---\n\n## Detailed Threats\n\n"
        
        # Sort by severity (Critical first) then by ID
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        sorted_threats = sorted(
            self.threats,
            key=lambda t: (severity_order.get(t.severity, 99), t.id)
        )
        
        for threat in sorted_threats:
            status_icon = {
                "Mitigated": "✅",
                "Partial": "⚠️",
                "Not Addressed": "❌"
            }.get(threat.status, "❓")
            
            report += f"""### {threat.id}: {threat.category}

**{threat.description}**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `{threat.affected_component}` |
| **Severity** | **{threat.severity}** |
| **Likelihood** | {threat.likelihood} |
| **OWASP LLM** | {threat.owasp_llm} |
| **Status** | {status_icon} {threat.status} |

**Mitigation:** {threat.mitigation}

---
"""
        
        return report
    
    def generate_json(self) -> str:
        """Generate JSON threat model for tooling."""
        return json.dumps(
            [asdict(t) for t in self.threats],
            indent=2
        )


def main():
    """Main entry point."""
    generator = ThreatModelGenerator()
    
    # Ensure output directory exists
    os.makedirs("docs/architecture", exist_ok=True)
    
    # Generate Markdown (use UTF-8 encoding for emoji support)
    with open("docs/architecture/threat-model.md", "w", encoding="utf-8") as f:
        f.write(generator.generate_markdown())
    print("[OK] docs/architecture/threat-model.md")
    
    # Generate JSON for tooling
    with open("docs/architecture/threat-model.json", "w", encoding="utf-8") as f:
        f.write(generator.generate_json())
    print("[OK] docs/architecture/threat-model.json")
    
    print("\n[SUMMARY]")
    print(f"   Total Threats: {len(generator.threats)}")
    mitigated = sum(1 for t in generator.threats if t.status == "Mitigated")
    partial = sum(1 for t in generator.threats if t.status == "Partial")
    not_addressed = sum(1 for t in generator.threats if t.status == "Not Addressed")
    print(f"   [OK] Mitigated: {mitigated}")
    print(f"   [WARN] Partial: {partial}")
    print(f"   [FAIL] Not Addressed: {not_addressed}")
    print(f"\n   Coverage: {mitigated}/{len(generator.threats)} ({mitigated*100//len(generator.threats)}%)")


if __name__ == "__main__":
    main()
