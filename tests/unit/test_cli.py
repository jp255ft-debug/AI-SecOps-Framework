"""Unit tests for guardrails/cli.py"""
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from guardrails.cli import run_audit, run_tests, main


class TestRunAudit:
    """Tests for run_audit function."""

    def test_run_audit_success(self):
        """Test successful audit execution returns 0."""
        with patch("guardrails.cli.Path.exists", return_value=True):
            with patch("guardrails.cli.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                result = run_audit(target="/tmp/test")
                assert result == 0

    def test_run_audit_with_output(self):
        """Test audit with custom output directory."""
        with patch("guardrails.cli.Path.exists", return_value=True):
            with patch("guardrails.cli.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                result = run_audit(target="/tmp/test", output="/tmp/output")
                assert result == 0

    def test_run_audit_failure(self):
        """Test audit failure returns non-zero."""
        with patch("guardrails.cli.Path.exists", return_value=True):
            with patch("guardrails.cli.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1)
                result = run_audit(target="/tmp/test")
                assert result == 1

    def test_run_audit_script_not_found(self):
        """Test audit when script doesn't exist returns 1."""
        with patch("guardrails.cli.Path.exists", return_value=False):
            result = run_audit(target="/tmp/test")
            assert result == 1


class TestRunTests:
    """Tests for run_tests function."""

    def test_run_tests_all(self):
        """Test running all tests."""
        with patch("guardrails.cli.Path.exists", return_value=True):
            with patch("guardrails.cli.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                result = run_tests(test_type="all")
                assert result == 0

    def test_run_tests_unit(self):
        """Test running unit tests only (no matching type, returns 0)."""
        result = run_tests(test_type="unit")
        assert result == 0

    def test_run_tests_integration(self):
        """Test running integration tests only (no matching type, returns 0)."""
        result = run_tests(test_type="integration")
        assert result == 0

    def test_run_tests_prompts(self):
        """Test running prompt tests only."""
        with patch("guardrails.cli.Path.exists", return_value=True):
            with patch("guardrails.cli.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                result = run_tests(test_type="prompts")
                assert result == 0

    def test_run_tests_models(self):
        """Test running model tests only."""
        with patch("guardrails.cli.Path.exists", return_value=True):
            with patch("guardrails.cli.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                result = run_tests(test_type="models")
                assert result == 0


class TestMain:
    """Tests for main CLI entry point."""

    def test_main_audit(self):
        """Test main with --audit flag."""
        with patch.object(sys, "argv", ["ai-secops-audit", "--audit"]):
            with patch("guardrails.cli.run_audit", return_value=0):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0

    def test_main_audit_with_target(self):
        """Test main with --audit and --target."""
        with patch.object(sys, "argv", ["ai-secops-audit", "--audit", "--target", "/tmp"]):
            with patch("guardrails.cli.run_audit", return_value=0):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0

    def test_main_test(self):
        """Test main with --test flag."""
        with patch.object(sys, "argv", ["ai-secops-audit", "--test", "all"]):
            with patch("guardrails.cli.run_tests", return_value=0):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0

    def test_main_version(self):
        """Test main with --version flag."""
        with patch.object(sys, "argv", ["ai-secops-audit", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_main_no_args(self):
        """Test main with no arguments shows help."""
        with patch.object(sys, "argv", ["ai-secops-audit"]):
            with patch("guardrails.cli.argparse.ArgumentParser.print_help") as mock_help:
                result = main()
                assert result is None
                mock_help.assert_called_once()
