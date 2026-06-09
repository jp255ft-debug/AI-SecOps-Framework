# Architecture Overview - AI-SecOps-Framework

## System Context

The AI-SecOps-Framework is a DevSecOps auditing framework for LLM/ML infrastructures. It orchestrates multiple security tools to provide comprehensive security analysis in under 60 minutes.

## Architecture Diagram

See [system-context.mermaid](system-context.mermaid) for the system context diagram.

## Core Components

### 1. CLI Entry Point (`guardrails/cli.py`)
- Entry point: `ai-secops-audit`
- Parses command-line arguments
- Orchestrates audit phases

### 2. Audit Orchestrator (`scripts/run_audit_60min.sh`)
- 5 phases: Setup → SAST → SCA → LLM Tests → Report
- Each phase has a time budget
- Graceful degradation if tools are missing

### 3. SAST Engine (Semgrep)
- 13 custom rules mapped to OWASP LLM01-LLM10
- Rules in `config/semgrep/custom_rules.yaml`
- Output: JSON results

### 4. SCA Engine (Trivy)
- Scans for vulnerabilities, secrets, misconfigurations
- Configuration in `config/trivy/.trivyignore`
- Output: JSON results

### 5. LLM Security Tests
- Giskard: OWASP LLM vulnerability tests
- Promptfoo: Prompt injection tests (18 payloads)
- Output: JSON results

### 6. Runtime Guardrails (`guardrails/interceptor.py`)
- Input validation (prompt injection, length limits)
- Output validation (blocked patterns, sensitive data)
- Sanitization (remove blocked patterns)
- NeMo Guardrails integration

### 7. Report Generator
- Consolidates all scan results
- Generates Markdown report
- Risk scoring and recommendations

## Data Flow

```
User Input → CLI → Audit Script → Parallel Scans → Results → Report
                ↓                    ↓
         OpenTelemetry          Artifacts
         (Traces/Metrics)       (JSON files)
```

## Security Boundaries

1. **Input Boundary**: CLI arguments, LLM prompts
2. **Output Boundary**: Audit reports, LLM responses
3. **Storage Boundary**: Audit outputs (gitignored)
4. **Network Boundary**: LLM API calls, package registries

## Deployment Options

1. **Local**: `make audit` (requires tools installed)
2. **Docker**: `docker run ai-secops-framework:latest`
3. **CI/CD**: GitHub Actions workflows
4. **SaaS**: (Future) Managed service with API

## Observability

- **Tracing**: OpenTelemetry → Jaeger
- **Metrics**: OpenTelemetry → Prometheus → Grafana
- **Logging**: Structured JSON logs (structlog)

## Supply Chain Security

- **SBOM**: CycloneDX + SPDX formats
- **Signing**: Sigstore (keyless signing)
- **Scorecard**: OpenSSF Scorecard
- **Dependencies**: Dependabot (weekly updates)
