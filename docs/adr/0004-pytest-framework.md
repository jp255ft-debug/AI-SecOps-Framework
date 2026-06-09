# ADR 0004: Use Pytest for Testing Framework

## Status

Accepted (2026-06-08)

## Context

We need a testing framework that supports:
- Unit tests (fast, no external dependencies)
- Integration tests (bash scripts, CLI tools)
- Coverage reporting
- CI/CD integration
- Parameterized testing for security payloads

**Requirements:**
- Must be Python-native
- Must support fixtures and conftest.py
- Must produce JUnit XML for CI
- Must support coverage tracking

## Decision

Use **Pytest** as our testing framework.

**Implementation:**
- `pytest.ini` with coverage configuration
- `tests/unit/` for fast unit tests
- `tests/integration/` for bash script tests
- `tests/models/` for Giskard LLM tests
- `tests/fuzz/` for fuzz testing (Atheris)

## Consequences

### Pros

✅ Industry standard for Python testing
✅ Rich plugin ecosystem (coverage, timeout, xdist)
✅ Fixture system for reusable test setup
✅ Excellent CI/CD integration
✅ Parameterized testing for security payloads

### Cons

❌ Slower than unittest for very large test suites
❌ Fixture scoping can be confusing
❌ Some plugins have compatibility issues

## Alternatives Considered

1. **unittest**
   - Rejected: More verbose, less flexible, no built-in coverage

2. **nose2**
   - Rejected: Smaller community, slower development

3. **tox**
   - Rejected: Environment management tool, not a test framework

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Coverage](https://pytest-cov.readthedocs.io/)
- [Testing Python](https://docs.python-guide.org/writing/tests/)
