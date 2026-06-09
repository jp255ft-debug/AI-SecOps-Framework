#!/usr/bin/env python3
"""
AI-SecOps-Framework CLI
Entry point for command-line usage via `ai-secops-audit` or `python -m guardrails`.
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_audit(target: str, output: str | None = None) -> int:
    """Execute the full audit pipeline."""
    script = Path(__file__).parent.parent / "scripts" / "run_audit_60min.sh"
    
    if not script.exists():
        print(f"❌ Audit script not found: {script}")
        return 1
    
    cmd = ["bash", str(script), "--target", target]
    if output:
        cmd.extend(["--output-dir", output])
    
    print(f"🔍 Starting AI-SecOps audit...")
    print(f"   Target: {target}")
    print(f"   Script: {script}")
    print()
    
    result = subprocess.run(cmd)
    return result.returncode


def run_tests(test_type: str = "all") -> int:
    """Run security tests (prompt injection, model tests)."""
    project_dir = Path(__file__).parent.parent
    
    if test_type in ("all", "prompts"):
        promptfoo_dir = project_dir / "tests" / "prompt_injection"
        if (promptfoo_dir / "promptfoo.yaml").exists():
            print("🧪 Running prompt injection tests...")
            subprocess.run(
                ["npx", "promptfoo", "eval", "--config", "promptfoo.yaml"],
                cwd=promptfoo_dir,
            )
    
    if test_type in ("all", "models"):
        model_test = project_dir / "tests" / "models" / "test_giskard_vulns.py"
        if model_test.exists():
            print("🧪 Running model vulnerability tests...")
            subprocess.run(["python", str(model_test)])
    
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI-SecOps-Framework: DevSecOps auditing for LLM/ML infrastructures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-secops-audit --audit
  ai-secops-audit --audit --target /path/to/project
  ai-secops-audit --test prompts
  ai-secops-audit --version
        """,
    )
    
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Run full 60-minute security audit",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=str(Path.cwd()),
        help="Target directory to audit (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory for audit results",
    )
    parser.add_argument(
        "--test",
        type=str,
        choices=["all", "prompts", "models"],
        help="Run security tests (prompt injection, model vulnerabilities)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="AI-SecOps-Framework 1.0.0",
    )
    
    args = parser.parse_args()
    
    if args.audit:
        sys.exit(run_audit(args.target, args.output))
    elif args.test:
        sys.exit(run_tests(args.test))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
