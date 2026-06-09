"""Unit tests for scripts/sign_reports.py"""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.sign_reports import (
    generate_key,
    sign_report,
    verify_report,
    save_signature,
    load_signature,
    main,
)


class TestGenerateKey:
    """Tests for generate_key function."""

    def test_generate_key_default_length(self):
        """Test key generation with default length (32 bytes = 64 hex chars)."""
        key = generate_key()
        assert len(key) == 64  # 32 bytes * 2 hex chars per byte
        assert isinstance(key, str)

    def test_generate_key_custom_length(self):
        """Test key generation with custom length."""
        key = generate_key(length=16)
        assert len(key) == 32  # 16 bytes * 2 hex chars per byte

    def test_generate_key_uniqueness(self):
        """Test that generated keys are unique."""
        keys = {generate_key() for _ in range(100)}
        assert len(keys) == 100  # All unique

    def test_generate_key_hex_chars_only(self):
        """Test that key contains only valid hex characters."""
        key = generate_key()
        assert all(c in '0123456789abcdef' for c in key)


class TestSignReport:
    """Tests for sign_report function."""

    def test_sign_report_basic(self):
        """Test signing a report file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Report\n\nThis is a test.")
            f.flush()
            fname = f.name
        
        try:
            signature = sign_report(fname, "my-secret-key")
            assert isinstance(signature, str)
            assert len(signature) == 64  # SHA256 hex digest
        finally:
            os.unlink(fname)

    def test_sign_report_empty_file(self):
        """Test signing an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            fname = f.name
        
        try:
            signature = sign_report(fname, "my-secret-key")
            assert isinstance(signature, str)
            assert len(signature) == 64
        finally:
            os.unlink(fname)

    def test_sign_report_large_file(self):
        """Test signing a large file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("x" * 1000000)  # 1MB
            f.flush()
            fname = f.name
        
        try:
            signature = sign_report(fname, "my-secret-key")
            assert isinstance(signature, str)
            assert len(signature) == 64
        finally:
            os.unlink(fname)

    def test_sign_report_nonexistent_file(self):
        """Test signing a nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            sign_report("/nonexistent/report.md", "my-secret-key")

    def test_sign_report_deterministic(self):
        """Test that same input produces same signature."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            sig1 = sign_report(fname, "my-secret-key")
            sig2 = sign_report(fname, "my-secret-key")
            assert sig1 == sig2
        finally:
            os.unlink(fname)

    def test_sign_report_different_keys(self):
        """Test that different keys produce different signatures."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            sig1 = sign_report(fname, "key-1")
            sig2 = sign_report(fname, "key-2")
            assert sig1 != sig2
        finally:
            os.unlink(fname)


class TestVerifyReport:
    """Tests for verify_report function."""

    def test_verify_valid_signature(self):
        """Test verification of a valid signature."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            signature = sign_report(fname, "my-secret-key")
            assert verify_report(fname, signature, "my-secret-key") is True
        finally:
            os.unlink(fname)

    def test_verify_invalid_signature(self):
        """Test verification of an invalid signature."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            assert verify_report(fname, "invalid-signature", "my-secret-key") is False
        finally:
            os.unlink(fname)

    def test_verify_wrong_key(self):
        """Test verification with wrong key."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            signature = sign_report(fname, "correct-key")
            assert verify_report(fname, signature, "wrong-key") is False
        finally:
            os.unlink(fname)

    def test_verify_tampered_file(self):
        """Test verification of a tampered file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Original content")
            f.flush()
            fname = f.name
        
        try:
            signature = sign_report(fname, "my-secret-key")
            
            # Tamper with the file
            with open(fname, 'w') as f:
                f.write("Tampered content")
            
            assert verify_report(fname, signature, "my-secret-key") is False
        finally:
            os.unlink(fname)

    def test_verify_nonexistent_file(self):
        """Test verification of a nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            verify_report("/nonexistent/report.md", "signature", "key")


class TestSaveLoadSignature:
    """Tests for save_signature and load_signature functions."""

    def test_save_signature(self):
        """Test saving signature to .sig file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            signature = sign_report(fname, "my-secret-key")
            sig_path = save_signature(fname, signature)
            
            assert sig_path.endswith('.md.sig')
            assert Path(sig_path).exists()
            
            with open(sig_path, 'r') as f:
                data = json.load(f)
            
            assert data["algorithm"] == "HMAC-SHA256"
            assert data["signature"] == signature
            assert data["file"] == Path(fname).name
        finally:
            os.unlink(fname)
            sig_file = fname + '.sig'
            if os.path.exists(sig_file):
                os.unlink(sig_file)

    def test_load_signature(self):
        """Test loading signature from .sig file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            signature = sign_report(fname, "my-secret-key")
            sig_path = save_signature(fname, signature)
            
            loaded = load_signature(sig_path)
            assert loaded["signature"] == signature
            assert loaded["algorithm"] == "HMAC-SHA256"
        finally:
            os.unlink(fname)
            sig_file = fname + '.sig'
            if os.path.exists(sig_file):
                os.unlink(sig_file)

    def test_load_nonexistent_signature(self):
        """Test loading nonexistent .sig file raises error."""
        with pytest.raises(FileNotFoundError):
            load_signature("/nonexistent/file.md.sig")


class TestMain:
    """Tests for main CLI entry point."""

    def test_generate_key_command(self):
        """Test --generate-key command."""
        with patch.object(sys, 'argv', ['sign_reports.py', '--generate-key']):
            result = main()
            assert result == 0

    def test_generate_key_custom_length(self):
        """Test --generate-key with custom length."""
        with patch.object(sys, 'argv', ['sign_reports.py', '--generate-key', '--key-length', '16']):
            result = main()
            assert result == 0

    def test_sign_command(self):
        """Test --sign command."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            with patch.object(sys, 'argv', ['sign_reports.py', '--sign', fname, '--key', 'test-key']):
                result = main()
                assert result == 0
        finally:
            os.unlink(fname)

    def test_sign_missing_key(self):
        """Test --sign without --key returns error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            with patch.object(sys, 'argv', ['sign_reports.py', '--sign', fname]):
                result = main()
                assert result == 1
        finally:
            os.unlink(fname)

    def test_sign_nonexistent_file(self):
        """Test --sign with nonexistent file returns error."""
        with patch.object(sys, 'argv', ['sign_reports.py', '--sign', '/nonexistent.md', '--key', 'key']):
            result = main()
            assert result == 1

    def test_verify_valid(self):
        """Test --verify with valid signature."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            signature = sign_report(fname, "test-key")
            with patch.object(sys, 'argv', [
                'sign_reports.py', '--verify', fname, '--key', 'test-key', '--signature', signature
            ]):
                result = main()
                assert result == 0
        finally:
            os.unlink(fname)

    def test_verify_invalid(self):
        """Test --verify with invalid signature."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            with patch.object(sys, 'argv', [
                'sign_reports.py', '--verify', fname, '--key', 'test-key', '--signature', 'invalid'
            ]):
                result = main()
                assert result == 1
        finally:
            os.unlink(fname)

    def test_verify_missing_signature(self):
        """Test --verify without signature returns error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            with patch.object(sys, 'argv', ['sign_reports.py', '--verify', fname, '--key', 'test-key']):
                result = main()
                assert result == 1
        finally:
            os.unlink(fname)

    def test_verify_with_sig_file(self):
        """Test --verify using --sig-file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Test content")
            f.flush()
            fname = f.name
        
        try:
            signature = sign_report(fname, "test-key")
            sig_path = save_signature(fname, signature)
            
            with patch.object(sys, 'argv', [
                'sign_reports.py', '--verify', fname, '--key', 'test-key', '--sig-file', sig_path
            ]):
                result = main()
                assert result == 0
        finally:
            os.unlink(fname)
            sig_file = fname + '.sig'
            if os.path.exists(sig_file):
                os.unlink(sig_file)
