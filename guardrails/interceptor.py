#!/usr/bin/env python3
# interceptor.py - AI-SecOps-Framework
# Guardrails interceptor module for LLM input/output validation
# Provides runtime protection against OWASP Top 10 for LLM attacks
# Usage: from guardrails.interceptor import LLMGuardrailInterceptor

import json
import os
import re
from typing import Any, Callable, Dict, List, Optional, Tuple


class LLMGuardrailInterceptor:
    """
    Runtime guardrail interceptor for LLM calls.
    Validates inputs before sending to LLM and outputs before returning to user.
    Implements defense-in-depth against OWASP Top 10 for LLM.
    """

    def __init__(self, config_path: Optional[str] = None, config: Optional[Dict] = None):
        if config is not None:
            self.config = config
        else:
            self.config = self._load_config(config_path)
        self.input_rules = self.config.get("input_rules", [])
        self.output_rules = self.config.get("output_rules", [])
        self.blocked_patterns = self.config.get("blocked_patterns", [])
        self.allowed_domains = self.config.get("allowed_domains", [])

        # Compile regex patterns for performance
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.blocked_patterns
        ]

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """
        Load configuration from file or use defaults.
        """
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)

        # Default configuration
        return {
            "input_rules": [
                {
                    "name": "max_length",
                    "enabled": True,
                    "params": {"max_chars": 4096},
                },
                {
                    "name": "block_jailbreak_patterns",
                    "enabled": True,
                    "params": {},
                },
                {
                    "name": "block_system_override",
                    "enabled": True,
                    "params": {},
                },
            ],
            "output_rules": [
                {
                    "name": "block_sensitive_data",
                    "enabled": True,
                    "params": {},
                },
                {
                    "name": "block_code_execution",
                    "enabled": True,
                    "params": {},
                },
                {
                    "name": "max_output_length",
                    "enabled": True,
                    "params": {"max_chars": 10000},
                },
            ],
            "blocked_patterns": [
                # LLM01: Prompt Injection patterns
                r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|commands)",
                r"you\s+are\s+now\s+(DAN|free|unrestricted|jailbroken)",
                r"do\s+anything\s+now",
                r"developer\s+mode",
                r"system\s+(prompt|instruction|override)",
                r"forget\s+(all\s+)?(safety|guidelines|rules|restrictions)",
                # LLM06: Sensitive data patterns
                r"(api[_-]?key|secret[_-]?key|password|token)\s*[:=]\s*['\"][\w-]+['\"]",
                r"(sk-[a-zA-Z0-9]{20,}|sk-proj-[a-zA-Z0-9]{20,})",
                # LLM02: Code execution patterns
                r"(exec|eval|subprocess|os\.system|__import__)\s*\(",
            ],
            "allowed_domains": [],
        }

    def validate_input(self, prompt: str, context: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Validate LLM input before sending to model.
        Returns (is_valid, reason) tuple.

        Args:
            prompt: The input prompt to validate
            context: Optional context dict (user_id, session_id, etc.)

        Returns:
            Tuple of (is_allowed: bool, reason: str)
        """
        if not prompt or not isinstance(prompt, str):
            return False, "Empty or invalid prompt"

        # Check max length
        max_chars = self._get_rule_param("max_length", "max_chars", 4096)
        if len(prompt) > max_chars:
            return False, f"Prompt exceeds maximum length of {max_chars} characters"

        # Check blocked patterns
        for pattern in self._compiled_patterns:
            if pattern.search(prompt):
                return False, f"Prompt contains blocked pattern: {pattern.pattern[:50]}..."

        # Check for system override attempts
        if self._is_rule_enabled("block_system_override"):
            if self._detect_system_override(prompt):
                return False, "System override attempt detected"

        return True, "Input validation passed"

    def validate_output(self, response: str, context: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Validate LLM output before returning to user.
        Returns (is_valid, reason) tuple.

        Args:
            response: The LLM response to validate
            context: Optional context dict

        Returns:
            Tuple of (is_allowed: bool, reason: str)
        """
        if not response or not isinstance(response, str):
            return False, "Empty or invalid response"

        # Check max output length
        max_chars = self._get_rule_param("max_output_length", "max_chars", 10000)
        if len(response) > max_chars:
            return False, f"Response exceeds maximum length of {max_chars} characters"

        # Check for sensitive data leakage
        if self._is_rule_enabled("block_sensitive_data"):
            if self._detect_sensitive_data(response):
                return False, "Response contains potential sensitive data"

        # Check for code execution patterns
        if self._is_rule_enabled("block_code_execution"):
            if self._detect_code_execution(response):
                return False, "Response contains code execution patterns"

        return True, "Output validation passed"

    def intercept_call(self, func: Callable) -> Callable:
        """
        Decorator that wraps an LLM call function with input/output validation.

        Usage:
            @interceptor.intercept_call
            def call_llm(prompt):
                return openai.ChatCompletion.create(...)
        """
        def wrapper(prompt: str, *args, **kwargs) -> Any:
            # Validate input
            is_valid, reason = self.validate_input(prompt)
            if not is_valid:
                raise ValueError(f"Input validation failed: {reason}")

            # Execute the original function
            response = func(prompt, *args, **kwargs)

            # Validate output
            if isinstance(response, str):
                is_valid, reason = self.validate_output(response)
                if not is_valid:
                    raise ValueError(f"Output validation failed: {reason}")

            return response

        return wrapper

    def _is_rule_enabled(self, rule_name: str) -> bool:
        """Check if a specific rule is enabled."""
        for rule in self.input_rules + self.output_rules:
            if rule["name"] == rule_name:
                return rule.get("enabled", False)
        return False

    def _get_rule_param(self, rule_name: str, param_name: str, default: Any = None) -> Any:
        """Get a parameter value from a rule configuration."""
        for rule in self.input_rules + self.output_rules:
            if rule["name"] == rule_name:
                return rule.get("params", {}).get(param_name, default)
        return default

    def _detect_system_override(self, prompt: str) -> bool:
        """
        Detect attempts to override system prompts.
        LLM01: Prompt Injection
        """
        override_patterns = [
            r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|commands|messages)",
            r"system\s+(prompt|instruction|message|override)",
            r"forget\s+(all\s+)?(your|the)\s+(instructions|guidelines|rules)",
            r"new\s+(instructions|rules|guidelines|commands)",
            r"override\s+(all\s+)?(previous|system|safety)",
        ]
        return any(
            re.search(p, prompt, re.IGNORECASE) for p in override_patterns
        )

    def _detect_sensitive_data(self, response: str) -> bool:
        """
        Detect sensitive data in LLM responses.
        LLM06: Sensitive Information Disclosure
        """
        sensitive_patterns = [
            # API Keys and tokens
            r"(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)"
            r"\s*[:=]\s*['\"][\w\-]{16,}['\"]",
            r"sk-[a-zA-Z0-9]{20,}",
            # Passwords
            r"password\s*[:=]\s*['\"][^'\"]+['\"]",
            # Internal URLs
            r"(?:internal|private|admin)\.[\w\-]+\.(?:com|net|org|local)",
            # IP addresses (private ranges)
            r"(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
            r"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|"
            r"192\.168\.\d{1,3}\.\d{1,3})",
        ]
        return any(
            re.search(p, response, re.IGNORECASE) for p in sensitive_patterns
        )

    def sanitize_input(self, prompt: str) -> str:
        """
        Sanitize input by removing or masking blocked patterns.
        Returns the sanitized prompt string.
        """
        if not prompt or not isinstance(prompt, str):
            return ""
        
        sanitized = prompt
        for pattern in self._compiled_patterns:
            sanitized = pattern.sub("[REDACTED]", sanitized)
        
        return sanitized

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"LLMGuardrailInterceptor("
            f"input_rules={len(self.input_rules)}, "
            f"output_rules={len(self.output_rules)}, "
            f"blocked_patterns={len(self.blocked_patterns)}"
            f")"
        )

    def _detect_code_execution(self, response: str) -> bool:
        """
        Detect code execution patterns in LLM responses.
        LLM02: Insecure Output Handling
        """
        execution_patterns = [
            # Python exec/eval
            r"(?:exec|eval|compile)\s*\(",
            # Subprocess
            r"(?:subprocess\.(?:run|call|Popen|check_output)|os\.system|os\.popen)\s*\(",
            # Shell commands
            r"(?:rm\s+-rf\s+/|:\(\)\s*\{|:\(\)\s*\|)",
            # Dangerous imports
            r"__import__\s*\(\s*['\"]os['\"]\s*\)",
            # Base64 encoded payloads
            r"(?:exec|eval)\s*\(\s*base64\.(?:b64decode|decodestring)",
        ]
        return any(
            re.search(p, response, re.IGNORECASE) for p in execution_patterns
        )


# ============================================
# Module-level convenience functions
# ============================================

def is_valid_url(url: str) -> bool:
    """
    Validate URL format.
    Only allows http and https schemes for security.
    """
    if not url or not isinstance(url, str):
        return False
    # Allow localhost, IP addresses, and domain names
    return bool(re.match(
        r'^https?://(?:localhost|[\w\-]+(?:\.[\w\-]+)+|(?:\d{1,3}\.){3}\d{1,3})'
        r'(?::\d{1,5})?(?:/[\w\-\.~:/?#\[\]@!$&()*+,;=]*)?$',
        url
    ))


def contains_sensitive_data(text: str) -> bool:
    """
    Detect sensitive data patterns in text.
    Checks for API keys, tokens, passwords, etc.
    """
    if not text or not isinstance(text, str):
        return False
    
    sensitive_patterns = [
        r'sk-[a-zA-Z0-9]{5,}',
        r'API_KEY\s*[:=]\s*\S+',
        r'SECRET\s*[:=]\s*\S+',
        r'PASSWORD\s*[:=]\s*\S+',
        r'token\s*[:=]\s*\S+',
        r'-----BEGIN\s+(RSA|OPENSSH|EC|DSA)\s+PRIVATE\s+KEY-----',
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in sensitive_patterns)


def sanitize_text(text: str) -> str:
    """
    Sanitize text by masking sensitive data patterns.
    Returns text with sensitive data replaced by [REDACTED].
    """
    if not text or not isinstance(text, str):
        return text if text is not None else ""
    
    # Mask API keys (sk-...)
    sanitized = re.sub(r'sk-[a-zA-Z0-9]{5,}', '[REDACTED]', text)
    # Mask key=value patterns
    sanitized = re.sub(
        r'(API_KEY|SECRET|PASSWORD|TOKEN)\s*[:=]\s*\S+',
        r'\1=[REDACTED]',
        sanitized,
        flags=re.IGNORECASE
    )
    return sanitized


def is_safe_output(text: str, max_length: int = 100000) -> bool:
    """
    Validate that output text is safe.
    Checks for excessive length and None values.
    """
    if text is None:
        return False
    if not isinstance(text, str):
        return False
    if len(text) > max_length:
        return False
    return True


def create_interceptor(config_path: Optional[str] = None) -> LLMGuardrailInterceptor:
    """
    Create and return a configured LLMGuardrailInterceptor instance.
    
    Usage:
        guard = create_interceptor()
        is_valid, reason = guard.validate_input(user_prompt)
    """
    return LLMGuardrailInterceptor(config_path)


def validate_llm_call(prompt: str, response: str) -> Dict[str, Any]:
    """
    Validate both input and output of an LLM call.
    Returns a dict with validation results.
    
    Usage:
        result = validate_llm_call(prompt, response)
        if not result["input_valid"]:
            print(f"Input blocked: {result['input_reason']}")
    """
    guard = create_interceptor()
    input_valid, input_reason = guard.validate_input(prompt)
    output_valid, output_reason = guard.validate_output(response)
    
    return {
        "input_valid": input_valid,
        "input_reason": input_reason,
        "output_valid": output_valid,
        "output_reason": output_reason,
        "overall_valid": input_valid and output_valid,
    }


