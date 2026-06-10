# Makefile - AI-SecOps-Framework
# Build and automation targets for DevSecOps auditing
# Usage: make [target]

.PHONY: help install audit report clean setup-env test-prompts docker-build sbom threat-model fuzz otel-up otel-down sign-verify setup-tools

help:
	@echo "AI-SecOps-Framework - Available Targets"
	@echo "========================================"
	@echo "make install       Install all dependencies (Python + tools)"
	@echo "make setup-env     Setup environment (directories, hooks)"
	@echo "make setup-tools   Install external tools (promptfoo, ollama, zstd)"
	@echo "make audit         Run full 60-minute security audit"
	@echo "make report        Show latest audit report"
	@echo "make test-prompts  Run prompt injection tests"
	@echo "make docker-build  Build Docker image"
	@echo "make clean         Clean output directories"
	@echo "make help          Show this help message"

# Install all dependencies
install:
	@echo "Installing Python dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "Done."

# Setup environment
setup-env:
	@echo "Setting up environment..."
	bash scripts/setup_env.sh
	@echo "Done."

# Setup external tools (promptfoo, ollama, zstd)
setup-tools:
	@echo "Setting up external tools..."
	bash scripts/setup_tools.sh
	@echo "Done."

# Run full audit
audit:
	@echo "Starting 60-minute security audit..."
	bash scripts/run_audit_60min.sh
	@echo "Audit complete."

# Show latest report
report:
	@echo "=== Latest Audit Report ==="
	@if [ -f audits/outputs/latest/FINAL_REPORT.md ]; then \
		cat audits/outputs/latest/FINAL_REPORT.md; \
	else \
		echo "No audit reports found. Run 'make audit' first."; \
	fi

# Run prompt injection tests
test-prompts:
	@echo "Running prompt injection tests..."
	@if [ -f tests/prompt_injection/promptfoo.yaml ]; then \
		cd tests/prompt_injection && npx promptfoo eval --config promptfoo.yaml; \
	else \
		echo "Promptfoo config not found. Skipping."; \
	fi

# Build Docker image
docker-build:
	@echo "Building Docker image..."
	docker build -t ai-secops-framework:latest .
	@echo "Done."

# Generate SBOM and VEX documents
sbom:
	@echo "Generating SBOM and VEX documents..."
	bash scripts/generate_vex_sbom.sh
	@echo "Done."

# Generate threat model
threat-model:
	@echo "Generating threat model (STRIDE)..."
	python scripts/generate_threat_model.py
	@echo "Done."

# Run fuzz tests
fuzz:
	@echo "Running fuzz tests..."
	python -m pytest tests/fuzz/ -v --timeout=60
	@echo "Done."

# Start OpenTelemetry stack
otel-up:
	@echo "Starting OpenTelemetry stack (Jaeger + Prometheus + Grafana)..."
	docker compose -f docker-compose.otel.yml up -d
	@echo "Done. Jaeger: http://localhost:16686 | Grafana: http://localhost:3000"

# Stop OpenTelemetry stack
otel-down:
	@echo "Stopping OpenTelemetry stack..."
	docker compose -f docker-compose.otel.yml down
	@echo "Done."

# Sign a report
sign-report:
	@echo "Signing report..."
	@if [ -z "$(REPORT)" ]; then \
		echo "Usage: make sign-report REPORT=path/to/report.md KEY=your-key"; \
		exit 1; \
	fi
	python scripts/sign_reports.py --sign "$(REPORT)" --key "$(KEY)" --save-sig
	@echo "Done."

# Verify a report signature
verify-report:
	@echo "Verifying report signature..."
	@if [ -z "$(REPORT)" ]; then \
		echo "Usage: make verify-report REPORT=path/to/report.md KEY=your-key"; \
		exit 1; \
	fi
	python scripts/sign_reports.py --verify "$(REPORT)" --key "$(KEY)" --sig-file "$(REPORT).sig"
	@echo "Done."

# Generate a signing key
generate-key:
	@echo "Generating signing key..."
	python scripts/sign_reports.py --generate-key
	@echo "Done."

# Clean outputs
clean:
	@echo "Cleaning output directories..."
	rm -rf audits/outputs/*
	@echo "Done."
