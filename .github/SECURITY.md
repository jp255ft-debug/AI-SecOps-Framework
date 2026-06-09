# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**DO NOT** create public GitHub issues for security vulnerabilities.

If you discover a security vulnerability, please report it privately:

📧 **Email**: [security@ai-secops-framework.com](mailto:security@ai-secops-framework.com)

### What to Include

To help us respond quickly, please include:

1. **Description** - Type of vulnerability and potential impact
2. **Steps to Reproduce** - Minimal, complete, and reproducible steps
3. **Affected Versions** - Which versions are affected
4. **Suggested Fix** - If you have a proposed solution (optional)
5. **Proof of Concept** - If available (optional)

### Response Timeline

| Step | Timeframe |
|------|-----------|
| Acknowledgment | 48 hours |
| Initial Assessment | 7 days |
| Fix Development | 14 days |
| Security Advisory | Upon fix release |

### Disclosure Policy

- We will acknowledge receipt within 48 hours
- We will provide an estimated timeline for a fix
- We will notify you when the fix is released
- We will credit you in the security advisory (if desired)
- We will request a CVE identifier

## Security Best Practices

When using AI-SecOps-Framework:

### 🔒 Repository Security
- Always use the latest version
- Never commit secrets, API keys, or credentials
- Use `.env` files for local configuration
- Enable 2FA on GitHub
- Review Dependabot alerts regularly

### 🛡️ Runtime Security
- Run audits in isolated environments (Docker)
- Validate all inputs to LLM endpoints
- Use guardrails in production deployments
- Monitor audit logs for anomalies

### 📦 Supply Chain Security
- Verify SBOM signatures before deployment
- Pin dependency versions in production
- Use `pip install -r requirements.txt --require-hashes`
- Regularly run `make audit` on your codebase

## Security Features

AI-SecOps-Framework includes built-in security features:

- ✅ **SAST**: Semgrep with 13 OWASP LLM rules
- ✅ **SCA**: Trivy vulnerability scanning
- ✅ **Secrets Detection**: Gitleaks in CI pipeline
- ✅ **Runtime Guardrails**: NeMo Guardrails integration
- ✅ **Prompt Injection Testing**: 18 payloads across 5 categories
- ✅ **Dependency Review**: Automated in PRs
- ✅ **Pre-commit Hooks**: Secret and conflict detection

## Hall of Fame

We thank the following individuals for responsibly disclosing vulnerabilities:

*(This list will be populated as reports are received)*

---

*Last updated: 2026-06-08*
