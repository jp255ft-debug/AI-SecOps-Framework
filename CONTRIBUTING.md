# Contributing to AI-SecOps-Framework

First off, thank you for considering contributing to AI-SecOps-Framework! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Security Policy](#security-policy)
- [Questions?](#questions)

## Code of Conduct

This project adheres to the [Contributor Covenant](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code. Please report unacceptable behavior to [contact@ai-secops-framework.com](mailto:contact@ai-secops-framework.com).

## Getting Started

### Prerequisites

- Python 3.10+
- Git
- Make (optional, for automation)

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/AI-SecOps-Framework.git
cd AI-SecOps-Framework

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
git config core.hooksPath .githooks
```

### Branch Naming Convention

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `chore/description` - Maintenance tasks
- `test/description` - Test additions/changes

## Development Process

1. **Pick an issue** - Check our [issues page](https://github.com/jp255ft-debug/AI-SecOps-Framework/issues)
2. **Create a branch** - `git checkout -b feature/your-feature`
3. **Make changes** - Follow coding standards below
4. **Write tests** - Ensure coverage doesn't decrease
5. **Run tests** - `pytest` must pass
6. **Commit** - Use conventional commits (see below)
7. **Push** - `git push origin feature/your-feature`
8. **Open a PR** - Against the `main` branch

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`

Examples:
```
feat(guardrails): add rate limiting for LLM calls
fix(audit): correct Semgrep output parsing
docs(readme): update installation instructions
test(interceptor): add unit tests for input validation
```

## Pull Request Process

1. **Ensure tests pass** - `pytest` must be green
2. **Update documentation** - If adding features
3. **Add changelog entry** - Update `CHANGELOG.md`
4. **Link related issues** - Use `Closes #123` in PR description
5. **Request review** - At least one maintainer review required
6. **Squash commits** - Before merge (if requested)

### PR Checklist

- [ ] Code follows project style (ruff compliant)
- [ ] Tests added/updated and passing
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated
- [ ] No new warnings or errors
- [ ] Security implications considered

## Coding Standards

### Python

- **Formatter**: [Black](https://black.readthedocs.io/) (line length: 100)
- **Linter**: [Ruff](https://docs.astral.sh/ruff/)
- **Type Hints**: Required for all public functions
- **Docstrings**: Google style

```python
def validate_input(prompt: str, max_length: int = 4096) -> tuple[bool, str]:
    """Validate LLM input prompt for security issues.
    
    Args:
        prompt: The input text to validate
        max_length: Maximum allowed prompt length
        
    Returns:
        Tuple of (is_valid: bool, reason: str)
        
    Raises:
        ValueError: If prompt is empty
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty")
    # Implementation...
```

### Shell Scripts

- Use `#!/bin/bash` with `set -euo pipefail`
- Prefer `[[ ]]` over `[ ]` for conditionals
- Use functions for reusable logic
- Include usage comment at top

### YAML/JSON

- 2-space indentation for YAML
- No trailing whitespace
- Include comments explaining complex configurations

## Testing Requirements

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=guardrails --cov-report=html

# Specific test file
pytest tests/unit/test_interceptor.py -v

# Integration tests
pytest tests/integration/ -v
```

### Test Coverage

- **Minimum**: 70% coverage for new code
- **Target**: 80%+ for core modules
- **Required**: 100% for security-critical functions

### Test Structure

```
tests/
├── unit/           # Unit tests (fast, no external deps)
│   ├── test_interceptor.py
│   └── test_validators.py
├── integration/    # Integration tests (may need tools)
│   └── test_audit_script.py
└── models/         # Model security tests (Giskard)
    └── test_giskard_vulns.py
```

## Security Policy

### Reporting Vulnerabilities

**DO NOT** create public issues for security vulnerabilities.

Please report security vulnerabilities privately to:
**[security@ai-secops-framework.com](mailto:security@ai-secops-framework.com)**

See our [SECURITY.md](.github/SECURITY.md) for full details.

### Security Best Practices

- Never commit secrets, API keys, or credentials
- Use `.env` files for local configuration
- Run `make audit` before submitting PRs
- Review Dependabot alerts regularly

## Questions?

- **Issues**: [GitHub Issues](https://github.com/jp255ft-debug/AI-SecOps-Framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jp255ft-debug/AI-SecOps-Framework/discussions)
- **Email**: [contact@ai-secops-framework.com](mailto:contact@ai-secops-framework.com)

---

*Thank you for contributing to making AI infrastructure more secure! 🔒*
