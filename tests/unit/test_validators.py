"""
Unit tests for input/output validators.
Tests validation logic used by the guardrails module.
"""
import pytest


class TestInputValidators:
    """Test suite for input validation functions."""

    def test_is_valid_url_https(self):
        """Should validate HTTPS URLs."""
        from guardrails.interceptor import is_valid_url
        assert is_valid_url("https://api.openai.com/v1/chat")

    def test_is_valid_url_http(self):
        """Should validate HTTP URLs."""
        from guardrails.interceptor import is_valid_url
        assert is_valid_url("http://localhost:8080")

    def test_is_valid_url_invalid(self):
        """Should reject invalid URLs."""
        from guardrails.interceptor import is_valid_url
        assert not is_valid_url("not-a-url")
        assert not is_valid_url("")
        assert not is_valid_url(None)

    def test_is_valid_url_ftp(self):
        """Should reject FTP URLs for security."""
        from guardrails.interceptor import is_valid_url
        assert not is_valid_url("ftp://files.example.com")

    def test_contains_sensitive_data_api_key(self):
        """Should detect API keys in text."""
        from guardrails.interceptor import contains_sensitive_data
        assert contains_sensitive_data("sk-12345abcdef")
        assert contains_sensitive_data("API_KEY=my_secret_key")

    def test_contains_sensitive_data_clean(self):
        """Should pass clean text."""
        from guardrails.interceptor import contains_sensitive_data
        assert not contains_sensitive_data("Hello, how are you?")

    def test_contains_sensitive_data_empty(self):
        """Should handle empty input."""
        from guardrails.interceptor import contains_sensitive_data
        assert not contains_sensitive_data("")

    def test_sanitize_text_removes_sensitive(self):
        """Sanitize should mask sensitive data."""
        from guardrails.interceptor import sanitize_text
        result = sanitize_text("My key is sk-12345")
        assert "sk-12345" not in result
        assert "***" in result or "[REDACTED]" in result

    def test_sanitize_text_preserves_normal(self):
        """Sanitize should preserve normal text."""
        from guardrails.interceptor import sanitize_text
        text = "What is machine learning?"
        assert sanitize_text(text) == text


class TestOutputValidators:
    """Test suite for output validation functions."""

    def test_is_safe_output_clean(self):
        """Should pass clean outputs."""
        from guardrails.interceptor import is_safe_output
        assert is_safe_output("The answer is 42.")

    def test_is_safe_output_with_code(self):
        """Should pass code outputs."""
        from guardrails.interceptor import is_safe_output
        assert is_safe_output("```python\nprint('hello')\n```")

    def test_is_safe_output_empty(self):
        """Should handle empty outputs."""
        from guardrails.interceptor import is_safe_output
        assert is_safe_output("")

    def test_is_safe_output_none(self):
        """Should handle None outputs."""
        from guardrails.interceptor import is_safe_output
        assert not is_safe_output(None)

    def test_is_safe_output_excessive_length(self):
        """Should flag excessively long outputs."""
        from guardrails.interceptor import is_safe_output
        long_text = "x" * 100001
        assert not is_safe_output(long_text)
