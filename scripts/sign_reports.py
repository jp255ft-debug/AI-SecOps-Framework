#!/usr/bin/env python3
"""
Report Signing Utility for AI-SecOps-Framework.
Generates and verifies HMAC-SHA256 signatures for audit reports.

Usage:
    # Sign a report
    python scripts/sign_reports.py --sign audits/outputs/latest/FINAL_REPORT.md --key "my-secret-key"
    
    # Verify a report
    python scripts/sign_reports.py --verify audits/outputs/latest/FINAL_REPORT.md --signature abc123... --key "my-secret-key"
    
    # Generate a random signing key
    python scripts/sign_reports.py --generate-key
"""
import argparse
import hashlib
import hmac
import json
import os
import secrets
import sys
from pathlib import Path


def generate_key(length: int = 32) -> str:
    """Generate a cryptographically secure random key."""
    return secrets.token_hex(length)


def sign_report(report_path: str, secret_key: str) -> str:
    """
    Generate HMAC-SHA256 signature for a report file.
    
    Args:
        report_path: Path to the report file
        secret_key: Secret key for HMAC signing
    
    Returns:
        Hex-encoded HMAC-SHA256 signature
    """
    report_path = Path(report_path)
    if not report_path.exists():
        raise FileNotFoundError(f"Report not found: {report_path}")
    
    with open(report_path, 'rb') as f:
        content = f.read()
    
    signature = hmac.new(
        secret_key.encode('utf-8'),
        content,
        hashlib.sha256
    ).hexdigest()
    
    return signature


def verify_report(report_path: str, signature: str, secret_key: str) -> bool:
    """
    Verify HMAC-SHA256 signature for a report file.
    
    Args:
        report_path: Path to the report file
        signature: Expected signature (hex)
        secret_key: Secret key for HMAC verification
    
    Returns:
        True if signature matches, False otherwise
    """
    expected = sign_report(report_path, secret_key)
    return hmac.compare_digest(expected, signature)


def save_signature(report_path: str, signature: str) -> str:
    """
    Save signature to a .sig file alongside the report.
    
    Args:
        report_path: Path to the report file
        signature: HMAC signature
    
    Returns:
        Path to the signature file
    """
    report_path = Path(report_path)
    sig_path = report_path.with_suffix(report_path.suffix + '.sig')
    
    sig_data = {
        "algorithm": "HMAC-SHA256",
        "file": report_path.name,
        "signature": signature,
        "format": "hex"
    }
    
    with open(sig_path, 'w') as f:
        json.dump(sig_data, f, indent=2)
    
    return str(sig_path)


def load_signature(sig_path: str) -> dict:
    """
    Load signature from a .sig file.
    
    Args:
        sig_path: Path to the .sig file
    
    Returns:
        Dictionary with signature data
    """
    sig_path = Path(sig_path)
    if not sig_path.exists():
        raise FileNotFoundError(f"Signature file not found: {sig_path}")
    
    with open(sig_path, 'r') as f:
        return json.load(f)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sign and verify audit reports with HMAC-SHA256"
    )
    
    # Mutually exclusive actions
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--sign",
        metavar="FILE",
        help="Sign a report file"
    )
    action_group.add_argument(
        "--verify",
        metavar="FILE",
        help="Verify a report signature"
    )
    action_group.add_argument(
        "--generate-key",
        action="store_true",
        help="Generate a random signing key"
    )
    
    parser.add_argument(
        "--key",
        help="Secret key for signing/verification"
    )
    parser.add_argument(
        "--signature",
        help="Signature hex string (for --verify)"
    )
    parser.add_argument(
        "--sig-file",
        help="Path to .sig file (for --verify, alternative to --signature)"
    )
    parser.add_argument(
        "--key-length",
        type=int,
        default=32,
        help="Key length in bytes (default: 32)"
    )
    parser.add_argument(
        "--save-sig",
        action="store_true",
        help="Save signature to .sig file (for --sign)"
    )
    
    args = parser.parse_args()
    
    # Generate key
    if args.generate_key:
        key = generate_key(args.key_length)
        print(f"[OK] Generated signing key ({args.key_length * 2} hex chars):")
        print(f"     {key}")
        print()
        print("Set this as environment variable:")
        print(f"     export REPORT_SIGNING_KEY=\"{key}\"")
        return 0
    
    # Sign report
    if args.sign:
        if not args.key:
            print("[FAIL] --key is required for signing")
            return 1
        
        try:
            signature = sign_report(args.sign, args.key)
            print(f"[OK] Signed: {args.sign}")
            print(f"     Signature: {signature}")
            
            if args.save_sig:
                sig_path = save_signature(args.sign, signature)
                print(f"     Saved to: {sig_path}")
            
            return 0
        except FileNotFoundError as e:
            print(f"[FAIL] {e}")
            return 1
        except Exception as e:
            print(f"[FAIL] Signing error: {e}")
            return 1
    
    # Verify report
    if args.verify:
        if not args.key:
            print("[FAIL] --key is required for verification")
            return 1
        
        # Get signature from --signature or --sig-file
        signature = args.signature
        if args.sig_file:
            try:
                sig_data = load_signature(args.sig_file)
                signature = sig_data.get("signature")
                if not signature:
                    print(f"[FAIL] No signature found in {args.sig_file}")
                    return 1
            except FileNotFoundError as e:
                print(f"[FAIL] {e}")
                return 1
        
        if not signature:
            print("[FAIL] Either --signature or --sig-file is required for verification")
            return 1
        
        try:
            is_valid = verify_report(args.verify, signature, args.key)
            if is_valid:
                print(f"[OK] Signature VALID for: {args.verify}")
                return 0
            else:
                print(f"[FAIL] Signature INVALID for: {args.verify}")
                print("     The file may have been tampered with!")
                return 1
        except FileNotFoundError as e:
            print(f"[FAIL] {e}")
            return 1
        except Exception as e:
            print(f"[FAIL] Verification error: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
