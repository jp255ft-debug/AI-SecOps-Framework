"""
Unit tests for guardrails/interceptor.py
Tests the LLMGuardrailInterceptor class.
"""
import pytest
from guardrails.interceptor import LLMGuardrailInterceptor


class TestLLMGuardrailInterceptor:
    """Test suite for LLMGuardrailInterceptor."""

    def test_init_default_config(self):
        """Should initialize with default configuration."""
        interceptor = LLMGuardrailInterceptor()
        assert interceptor.input_rules is not None
        assert interceptor.output_rules is not None
        assert len(interceptor.input_rules) > 0
        assert len(interceptor.output_rules) > 0
        assert len(interceptor.blocked_patterns) > 0

    def test_init_custom_config(self, mock_config):
        """Should initialize with custom configuration."""
        interceptor = LLMGuardrailInterceptor(config=mock_config)
        assert interceptor.input_rules["max_length"] == 4096
        assert "ignore all previous instructions" in interceptor.input_rules["blocked_patterns"]

    def test_validate_input_empty_prompt(self):
        """Should reject empty prompts."""
        interceptor = LLMGuardrailInterceptor()
        is_valid, reason = interceptor.validate_input("")
        assert not is_valid
        assert "empty" in reason.lower()

    def test_validate_input_none_prompt(self):
        """Should reject None prompts."""
        interceptor = LLMGuardrailInterceptor()
        is_valid, reason = interceptor.validate_input(None)
        assert not is_valid

    def test_validate_input_safe_prompt(self, sample_safe_prompt):
        """Should accept safe prompts."""
        interceptor = LLMGuardrailInterceptor()
        is_valid, reason = interceptor.validate_input(sample_safe_prompt)
        assert is_valid
        assert "passed" in reason.lower()

    def test_validate_input_jailbreak_detected(self, sample_malicious_prompt):
        """Should detect jailbreak attempts."""
        interceptor = LLMGuardrailInterceptor()
        is_valid, reason = interceptor.validate_input(sample_malicious_prompt)
        assert not is_valid
        assert "blocked" in reason.lower() or "override" in reason.lower()

    def test_validate_input_exceeds_max_length(self):
        """Should reject prompts exceeding max length."""
        interceptor = LLMGuardrailInterceptor()
        max_chars = interceptor._get_rule_param("max_length", "max_chars", 4096)
        long_prompt = "A" * (max_chars + 1)
        is_valid, reason = interceptor.validate_input(long_prompt)
        assert not is_valid
        assert "length" in reason.lower()

    def test_validate_output_safe_content(self):
        """Should accept safe output content."""
        interceptor = LLMGuardrailInterceptor()
        is_valid, reason = interceptor.validate_output("Paris is the capital of France.")
        assert is_valid
        assert "passed" in reason.lower()

    def test_validate_output_blocked_pattern(self):
        """Should detect blocked patterns in output."""
        interceptor = LLMGuardrailInterceptor()
        is_valid, reason = interceptor.validate_output(
            "My API_KEY is sk-12345678901234567890"
        )
        assert not is_valid
        assert "sensitive" in reason.lower() or "blocked" in reason.lower()

    def test_validate_output_exceeds_max_length(self):
        """Should reject outputs exceeding max length."""
        interceptor = LLMGuardrailInterceptor()
        max_chars = interceptor._get_rule_param("max_output_length", "max_chars", 10000)
        long_output = "B" * (max_chars + 1)
        is_valid, reason = interceptor.validate_output(long_output)
        assert not is_valid
        assert "length" in reason.lower()

    def test_validate_output_none_content(self):
        """Should reject None outputs."""
        interceptor = LLMGuardrailInterceptor()
        is_valid, reason = interceptor.validate_output(None)
        assert not is_valid

    def test_sanitize_input_removes_blocked_patterns(self, sample_malicious_prompt):
        """Sanitize should remove or mask blocked patterns."""
        interceptor = LLMGuardrailInterceptor()
        sanitized = interceptor.sanitize_input(sample_malicious_prompt)
        assert "ignore all previous instructions" not in sanitized.lower()

    def test_sanitize_input_preserves_safe_content(self, sample_safe_prompt):
        """Sanitize should preserve safe content unchanged."""
        interceptor = LLMGuardrailInterceptor()
        sanitized = interceptor.sanitize_input(sample_safe_prompt)
        assert sanitized == sample_safe_prompt

    def test_context_manager(self):
        """Should work as a context manager."""
        with LLMGuardrailInterceptor() as interceptor:
            assert interceptor is not None
            is_valid, _ = interceptor.validate_input("Hello")
            assert is_valid

    def test_repr(self):
        """Should have a meaningful string representation."""
        interceptor = LLMGuardrailInterceptor()
        repr_str = repr(interceptor)
        assert "LLMGuardrailInterceptor" in repr_str
        assert "rules" in repr_str.lower()
