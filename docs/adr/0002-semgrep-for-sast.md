# ADR 0002: Use Semgrep for SAST Scanning

## Status

Accepted (2026-06-08)

## Context

We need static analysis security testing (SAST) for LLM/ML codebases. Requirements:
- Must support custom rules for OWASP LLM Top 10
- Must be fast enough for CI/CD integration (<5 min)
- Must support Python and Dockerfile scanning
- Must produce machine-readable output (JSON/SARIF)

## Decision

Use **Semgrep** as our SAST engine.

**Implementation:**
- 13 custom rules in `config/semgrep/custom_rules.yaml`
- Rules mapped to OWASP LLM01-LLM10
- Integrated into CI via `secure-ci.yml`
- Also available in local audit via `run_audit_60min.sh`

## Consequences

### Pros

✅ Custom rules for LLM-specific vulnerabilities
✅ Fast execution (seconds to minutes)
✅ SARIF output for GitHub Security Tab
✅ Active community with 2000+ community rules
✅ Free and open-source

### Cons

❌ Limited to pattern matching (no dataflow analysis)
❌ Requires rule maintenance as LLM frameworks evolve
❌ False positives need tuning

## Alternatives Considered

1. **CodeQL**
   - Rejected: Slower, harder to write custom rules, GitHub-only

2. **Bandit**
   - Rejected: Python-only, no LLM-specific rules, limited output formats

3. **SonarQube**
   - Rejected: Heavy infrastructure, requires database, overkill for CLI tool

## References

- [Semgrep Documentation](https://semgrep.dev/docs/)
- [OWASP LLM Top 10](https://genai.owasp.org/)
- [Custom Rules Guide](https://semgrep.dev/docs/writing-rules/overview/)
