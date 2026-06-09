# Threat Model - AI-SecOps-Framework

**Generated:** 2026-06-08 20:55:55
**Methodology:** STRIDE (adapted for LLM/ML systems)
**Total Threats:** 12

---

## Executive Summary

| Category | Count | ✅ Mitigated | ⚠️ Partial | ❌ Not Addressed |
|----------|-------|-------------|------------|------------------|
| Spoofing | 1 | 0 | 1 | 0 |
| Tampering | 2 | 0 | 0 | 2 |
| Repudiation | 1 | 0 | 0 | 1 |
| Information Disclosure | 3 | 3 | 0 | 0 |
| Denial of Service | 2 | 0 | 2 | 0 |
| Elevation of Privilege | 3 | 3 | 0 | 0 |
| **Total** | **12** | **6** | **3** | **3** |

### Risk Distribution

- **Critical**: ████░ (4)
- **High**: █████ (5)
- **Medium**: ██░░░ (2)
- **Low**: █░░░░ (1)

---

## Detailed Threats

### T005: Information Disclosure

**Prompt injection causes LLM to leak training data, system prompts, or sensitive business logic**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `LLM API Calls` |
| **Severity** | **Critical** |
| **Likelihood** | High |
| **OWASP LLM** | LLM01 |
| **Status** | ✅ Mitigated |

**Mitigation:** NeMo Guardrails input validation, Semgrep rules for prompt injection (LLM01), output sanitization

---
### T006: Information Disclosure

**Secrets (API keys, tokens) leaked in audit reports or logs**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `audits/outputs/*.md, logs` |
| **Severity** | **Critical** |
| **Likelihood** | Medium |
| **OWASP LLM** | LLM06 |
| **Status** | ✅ Mitigated |

**Mitigation:** Gitleaks scanning in CI, output sanitization in report generator, .gitignore for outputs/

---
### T007: Information Disclosure

**Sensitive data included in LLM prompts sent to external API providers**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `LLM API Client` |
| **Severity** | **Critical** |
| **Likelihood** | Medium |
| **OWASP LLM** | LLM06 |
| **Status** | ✅ Mitigated |

**Mitigation:** Semgrep rule llm-sensitive-data-in-prompt (LLM06), input sanitization, data classification

---
### T010: Elevation of Privilege

**LLM agent executes privileged commands (shell, filesystem) without authorization**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `LLM Tool Functions (@tool decorators)` |
| **Severity** | **Critical** |
| **Likelihood** | High |
| **OWASP LLM** | LLM07, LLM08 |
| **Status** | ✅ Mitigated |

**Mitigation:** Semgrep rules for @tool validation (LLM07), require human-in-the-loop (LLM08), sandbox execution

---
### T001: Spoofing

**Attacker spoofs LLM API responses to inject malicious content into the application**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `LLM API Client (openai, anthropic)` |
| **Severity** | **High** |
| **Likelihood** | Low |
| **OWASP LLM** | LLM02 |
| **Status** | ⚠️ Partial |

**Mitigation:** Use TLS pinning, verify API certificates, implement response validation with NeMo Guardrails

---
### T003: Tampering

**Attacker modifies Semgrep rules to suppress vulnerability detection**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `config/semgrep/custom_rules.yaml` |
| **Severity** | **High** |
| **Likelihood** | Low |
| **OWASP LLM** | N/A |
| **Status** | ❌ Not Addressed |

**Mitigation:** Code review on rule changes, sign rules with GPG, CI validation of rule integrity

---
### T008: Denial of Service

**Unbounded input causes LLM API cost explosion or resource exhaustion**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `LLM API Client` |
| **Severity** | **High** |
| **Likelihood** | Medium |
| **OWASP LLM** | LLM04 |
| **Status** | ⚠️ Partial |

**Mitigation:** Input length limits (4096 chars), rate limiting, cost monitoring, Semgrep rule llm-dos-unbounded-input

---
### T011: Elevation of Privilege

**LLM endpoint exposed without authentication allows model theft**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `LLM API Endpoints` |
| **Severity** | **High** |
| **Likelihood** | Medium |
| **OWASP LLM** | LLM10 |
| **Status** | ✅ Mitigated |

**Mitigation:** Semgrep rule llm-model-theft-exposed-endpoint (LLM10), API key authentication, rate limiting

---
### T012: Elevation of Privilege

**Dependency confusion attack installs malicious package during pip install**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `requirements.txt, pyproject.toml` |
| **Severity** | **High** |
| **Likelihood** | Medium |
| **OWASP LLM** | LLM05 |
| **Status** | ✅ Mitigated |

**Mitigation:** Pin dependency versions, use --require-hashes, Dependabot alerts, Trivy scanning

---
### T002: Tampering

**Attacker tampers with audit reports in storage to hide vulnerabilities**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `audits/outputs/` |
| **Severity** | **Medium** |
| **Likelihood** | Low |
| **OWASP LLM** | N/A |
| **Status** | ❌ Not Addressed |

**Mitigation:** Generate cryptographic signatures (HMAC-SHA256) for reports, use git for audit trail

---
### T009: Denial of Service

**Malicious payload causes Semgrep or Trivy to crash during audit**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `scripts/run_audit_60min.sh` |
| **Severity** | **Medium** |
| **Likelihood** | Low |
| **OWASP LLM** | N/A |
| **Status** | ⚠️ Partial |

**Mitigation:** Timeouts on all tool executions, graceful error handling, resource limits in Docker

---
### T004: Repudiation

**User denies running malicious audit command or accessing sensitive results**

| Attribute | Value |
|-----------|-------|
| **Affected Component** | `CLI (guardrails/cli.py)` |
| **Severity** | **Low** |
| **Likelihood** | Low |
| **OWASP LLM** | N/A |
| **Status** | ❌ Not Addressed |

**Mitigation:** Implement audit logging to syslog/CloudWatch, log all CLI invocations with user identity

---
