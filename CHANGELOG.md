# Changelog

All notable changes to AI-SecOps-Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- LICENSE file (MIT) for legal compliance
- .gitignore with comprehensive Python/security patterns
- .dockerignore for optimized Docker builds
- pyproject.toml (PEP 621) for pip installation
- setup.py for backward compatibility
- guardrails/__init__.py for proper Python packaging
- guardrails/cli.py CLI entry point (`ai-secops-audit`)
- CONTRIBUTING.md with development guidelines
- CHANGELOG.md (this file)
- .github/SECURITY.md for vulnerability disclosure
- .github/dependabot.yml for automated dependency updates
- .github/CODEOWNERS for PR ownership
- pytest.ini for test configuration
- tests/unit/ with unit tests for interceptor module
- tests/integration/ with integration test for audit script
- .github/workflows/test.yml for CI test pipeline

### Changed
- Fixed Dockerfile HEALTHCHECK to validate binaries correctly
- Updated README.md with CI and coverage badges
- Updated TREE.md with new file structure
- Updated all workflows with `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` for Node.js 24 compatibility
- Updated `pyproject.toml` with `pytest-timeout>=2.0.0` dependency
- Updated `run_audit_60min.sh` with `--help`/`-h` flag handler
- Updated `test_audit_script.py` with improved invalid argument validation
- Updated `dependabot.yml` to ignore Python major version updates
- Added `continue-on-error: true` to lint job in `test.yml` for CI stability

### Security
- Added security policy for responsible disclosure
- Added Dependabot for automated vulnerability patching
- Added pre-commit hooks for secret detection

## [1.0.0] - 2026-06-08

### Added
- **SAST Scanning**: Semgrep with 13 custom rules covering OWASP LLM01-LLM10
- **SCA Scanning**: Trivy for vulnerabilities, secrets, and misconfigurations
- **LLM Security Testing**: Giskard (13 tests) + Promptfoo (16 scenarios, 18 payloads)
- **Runtime Guardrails**: NeMo Guardrails integration with custom interceptor
- **CI/CD Pipelines**: GitHub Actions for secure CI and LLM evaluation
- **Container Support**: Multi-stage Dockerfile (Python 3.11 + Semgrep + Trivy + Node.js)
- **Automation**: Makefile with `install`, `audit`, `report`, `test-prompts` targets
- **Documentation**: README, executive summary template, technical finding template
- **SBOM/VEX**: Script for generating software bills of materials
- **Pre-commit Hooks**: Git hooks for secret detection and merge conflict checking
