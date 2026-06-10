# AI-SecOps-Framework - Estrutura do Projeto

```
AI-SecOps-Framework/
│
├── .ai/                           # Regras mestras do Cline
│   ├── claude_plan_rules.md       # Regras para modo PLAN
│   ├── deepseek_act_rules.md      # Regras para modo ACT
│   └── project_context.md         # Contexto do projeto
│
├── .github/                       # Configurações GitHub
│   ├── workflows/
│   │   ├── lint.yml               # Linting (Ruff + Black + MyPy)
│   │   ├── test.yml               # Testes unitários + integração
│   │   ├── secure-ci.yml          # Pipeline de segurança (SAST, SCA, Secrets)
│   │   ├── .llm-eval.yml.disabled # Avaliação de LLM (desabilitado temporariamente)
│   │   ├── sbom-release.yml       # Geração de SBOM + assinatura Sigstore
│   │   └── fuzz.yml               # Fuzzing contínuo (Atheris)
│   ├── SECURITY.md                # Política de segurança
│   ├── dependabot.yml             # Atualizações automáticas
│   └── CODEOWNERS                 # Ownership de código
│
├── .githooks/
│   └── pre-commit                 # Hook pre-commit
│
├── audits/
│   ├── outputs/                   # Relatórios de auditoria (gitignored)
│   └── templates/
│       ├── executive_summary.md   # Template de relatório executivo
│       └── technical_finding.md   # Template de achado técnico
│
├── config/
│   ├── semgrep/
│   │   └── custom_rules.yaml      # 13 regras OWASP LLM customizadas
│   ├── trivy/
│   │   └── .trivyignore           # Ignorar regras Trivy
│   ├── prometheus/
│   │   └── prometheus.yml         # Configuração Prometheus
│   └── otel-collector.yml         # Configuração OpenTelemetry Collector
│
├── docs/
│   ├── adr/
│   │   ├── README.md              # Índice de ADRs
│   │   ├── template.md            # Template para novos ADRs
│   │   ├── 0001-use-nemo-guardrails.md
│   │   ├── 0002-semgrep-for-sast.md
│   │   ├── 0003-trivy-for-sca.md
│   │   └── 0004-pytest-framework.md
│   ├── reports/
│   │   └── daily-report-2026-06-08.md  # Relatório diário 08/06
│   └── architecture/
│       ├── overview.md            # Visão geral da arquitetura
│       ├── system-context.mermaid # Diagrama C4 de contexto
│       ├── threat-model.md        # Modelo de ameaças STRIDE
│       └── threat-model.json      # Modelo de ameaças (JSON)
│
├── guardrails/
│   ├── __init__.py                # Inicialização do pacote
│   ├── cli.py                     # CLI entry point
│   ├── interceptor.py             # Módulo de interceptação LLM
│   ├── telemetry.py               # OpenTelemetry tracing/metrics
│   └── nemo_config/
│       ├── config.yaml            # Configuração NeMo Guardrails
│       └── rails.co               # Regras Colang
│
├── scripts/
│   ├── run_audit_60min.sh         # Script principal de auditoria
│   ├── setup_env.sh               # Setup do ambiente
│   ├── generate_vex_sbom.sh       # Geração de SBOM/VEX
│   ├── generate_threat_model.py   # Gerador de threat model STRIDE
│   └── sign_reports.py            # Assinatura HMAC-SHA256 de relatórios
│
├── tests/
│   ├── __init__.py
│   ├── unit/                      # Testes unitários
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_cli.py
│   │   ├── test_interceptor.py
│   │   ├── test_sign_reports.py
│   │   ├── test_telemetry.py
│   │   └── test_validators.py
│   ├── integration/               # Testes de integração
│   │   ├── __init__.py
│   │   └── test_audit_script.py
│   ├── models/                    # Testes Giskard
│   │   └── test_giskard_vulns.py
│   ├── prompt_injection/          # Testes Promptfoo
│   │   ├── promptfoo.yaml
│   │   └── payloads.json
│   └── fuzz/                      # Fuzzing (Atheris)
│       ├── __init__.py
│       └── test_interceptor_fuzz.py
│
├── .clinerules                    # Regras do Cline
├── .dockerignore
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── docker-compose.otel.yml        # Stack OpenTelemetry (Jaeger + Prometheus + Grafana)
├── Dockerfile                     # Container multi-stage
├── LICENSE                        # MIT License
├── Makefile                       # Automação de tarefas
├── pyproject.toml                 # Configuração Python moderna
├── pytest.ini                     # Configuração Pytest
├── README.md                      # Documentação principal
├── requirements.txt               # Dependências Python
├── setup.py                       # Setup legacy (compatibilidade)
└── TREE.md                        # Este arquivo
```
