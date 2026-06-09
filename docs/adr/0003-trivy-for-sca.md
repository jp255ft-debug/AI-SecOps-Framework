# ADR 0003: Use Trivy for SCA Scanning

## Status

Accepted (2026-06-08)

## Context

We need software composition analysis (SCA) to detect:
- Known vulnerabilities in Python dependencies
- Misconfigurations in Docker/Kubernetes
- Hardcoded secrets in codebase
- Supply chain attacks

**Requirements:**
- Must support multiple scanners (vuln, secret, misconfig)
- Must be embeddable in CI/CD and Docker
- Must produce JSON output for report generation
- Must support ignore rules for accepted risks

## Decision

Use **Aqua Security Trivy** as our SCA scanner.

**Implementation:**
- Filesystem scanning in CI via `secure-ci.yml`
- Docker scanning in `Dockerfile` build
- Ignore rules in `config/trivy/.trivyignore`
- Integrated into local audit via `run_audit_60min.sh`

## Consequences

### Pros

✅ All-in-one scanner (vulns, secrets, misconfigs)
✅ Fast scanning (seconds for small projects)
✅ Excellent Docker support
✅ Active development by Aqua Security
✅ SBOM generation support

### Cons

❌ Large database download on first run (~500MB)
❌ Some false positives in Go vulnerability matching
❌ Limited language support for deep analysis

## Alternatives Considered

1. **Snyk**
   - Rejected: Requires API key, rate-limited free tier, vendor lock-in

2. **Safety**
   - Rejected: Python-only, no secrets/misconfig scanning

3. **Grype**
   - Rejected: Less mature, smaller community, fewer integrations

## References

- [Trivy Documentation](https://trivy.dev/)
- [Aqua Security](https://www.aquasec.com/)
- [.trivyignore Reference](https://trivy.dev/docs/configuration/filtering/)
