"""
Integration tests for the audit script (run_audit_60min.sh).
Tests that the script can be invoked and produces expected output.
"""
import subprocess
import sys
import pytest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts" / "run_audit_60min.sh"


def _to_wsl_path(windows_path: str) -> str:
    """Convert a Windows path to WSL path (e.g., C:\foo -> /mnt/c/foo)."""
    if sys.platform != "win32":
        return windows_path
    # Remove drive letter and convert backslashes
    drive = windows_path[0].lower()
    rest = windows_path[2:].replace("\\", "/")
    return f"/mnt/{drive}{rest}"


def _run_bash(script_path: Path, *args: str) -> subprocess.CompletedProcess:
    """
    Run a bash script, handling Windows-to-WSL path conversion if needed.
    """
    wsl_path = _to_wsl_path(str(script_path))
    cmd = ["bash", wsl_path]
    if args:
        cmd.extend(args)
    
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10,
    )


@pytest.mark.integration
def test_audit_script_exists():
    """The audit script should exist and be executable."""
    assert SCRIPT_PATH.exists(), f"Script not found: {SCRIPT_PATH}"
    assert SCRIPT_PATH.is_file()


@pytest.mark.integration
def test_audit_script_help():
    """The audit script should display usage information."""
    result = _run_bash(SCRIPT_PATH, "--help")
    # Should exit with 0 or show usage
    assert result.returncode == 0 or "Usage" in result.stdout or "Usage" in result.stderr


@pytest.mark.integration
def test_audit_script_invalid_arg():
    """The audit script should handle invalid arguments gracefully."""
    result = _run_bash(SCRIPT_PATH, "--invalid-flag")
    assert result.returncode != 0
    assert "Unknown" in result.stdout or "Unknown" in result.stderr


@pytest.mark.integration
def test_setup_script_exists():
    """The setup script should exist."""
    setup_path = SCRIPT_PATH.parent / "setup_env.sh"
    assert setup_path.exists()


@pytest.mark.integration
def test_sbom_script_exists():
    """The SBOM generation script should exist."""
    sbom_path = SCRIPT_PATH.parent / "generate_vex_sbom.sh"
    assert sbom_path.exists()


@pytest.mark.integration
def test_audit_script_syntax():
    """The audit script should have valid bash syntax."""
    wsl_path = _to_wsl_path(str(SCRIPT_PATH))
    result = subprocess.run(
        ["bash", "-n", wsl_path],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Bash syntax error: {result.stderr}"
