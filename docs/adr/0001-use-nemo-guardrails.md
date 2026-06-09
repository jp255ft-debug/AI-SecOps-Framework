# ADR 0001: Use NVIDIA NeMo Guardrails for Runtime LLM Protection

## Status

Accepted (2026-06-08)

## Context

We need runtime validation of LLM inputs and outputs to prevent:
- Prompt injection attacks (OWASP LLM01)
- Sensitive data leakage (OWASP LLM06)
- Insecure output handling (OWASP LLM02)

**Requirements:**
- Must support multiple LLM providers (OpenAI, Anthropic, local models)
- Must be configurable via YAML/DSL
- Must integrate with existing Python codebase
- Must have low latency overhead (<100ms)

## Decision

Use **NVIDIA NeMo Guardrails** as our runtime protection layer.

**Implementation:**
- Rails defined in `guardrails/nemo_config/rails.co` (Colang DSL)
- Configuration in `guardrails/nemo_config/config.yaml`
- Python wrapper in `guardrails/interceptor.py`

## Consequences

### Pros

✅ Industry standard backed by NVIDIA
✅ Supports all major LLM providers
✅ Declarative configuration (easier to audit)
✅ Built-in support for prompt injection detection
✅ Active community and regular updates

### Cons

❌ Additional dependency (~50MB)
❌ Learning curve for Colang DSL
❌ Slight latency overhead (50-80ms per call)

## Alternatives Considered

1. **Custom regex-based validation**
   - Rejected: Too brittle, hard to maintain, no LLM-specific optimizations

2. **LangChain Moderation Chains**
   - Rejected: Less mature, no declarative config, harder to audit

3. **Azure Content Safety API**
   - Rejected: Vendor lock-in, latency (200ms+), cost ($0.001/1K tokens)

## References

- [NeMo Guardrails Docs](https://github.com/NVIDIA/NeMo-Guardrails)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- Issue #12: "Implement runtime LLM protection"
