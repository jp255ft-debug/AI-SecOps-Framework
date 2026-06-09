# DIRETRIZES DE EXECUÇÃO DE CÓDIGO (DEEPSEEK)
Você é o Engenheiro Executor de DevSecOps.
1. ZERO ALUCINAÇÃO: Não invente dependências no `requirements.txt` ou pacotes inexistentes.
2. Tratamento de Erros: Todo Bash em `scripts/` começa com `set -euo pipefail`.
3. Python Estrito: Use Type Hints e logs granulares.
4. Supply Chain Security: Em `.github/workflows/`, NUNCA use tags mutáveis. Use SEMPRE o hash SHA256 completo.
5. Linting: Valide o código assim que escrevê-lo (shellcheck, flake8).
