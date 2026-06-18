# Dockerfile - AI-SecOps-Framework
# Container image for portable DevSecOps auditing
# Build: docker build -t ai-secops-framework:latest .
# Run:   docker run --rm -v $(pwd):/workspace ai-secops-framework:latest

FROM python:3.14-slim AS base

# ============================================
# Stage 1: Base image with system dependencies
# ============================================
LABEL maintainer="AI-SecOps-Framework Team"
LABEL description="DevSecOps auditing framework for LLM/ML infrastructures"
LABEL version="1.0.0"

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Stage 2: Install security tools
# ============================================
FROM base AS tools

# Install Semgrep
RUN pip install semgrep>=1.60.0

# Install Trivy
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh \
    | sh -s -- -b /usr/local/bin v0.50.0

# Install Node.js for Promptfoo
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g promptfoo \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Stage 3: Application setup
# ============================================
FROM tools AS app

WORKDIR /workspace

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Create output directories
RUN mkdir -p audits/outputs

# Set default command
ENTRYPOINT ["bash", "scripts/run_audit_60min.sh"]
CMD ["--target", "/workspace"]

# ============================================
# Health check
# ============================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD semgrep --version > /dev/null 2>&1 && trivy --version > /dev/null 2>&1 && python3 --version > /dev/null 2>&1 && echo "All tools available" || exit 1
