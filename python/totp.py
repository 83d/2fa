#!/usr/bin/env python3
"""Generate the current six-digit TOTP code with PyOTP."""

import getpass

import pyotp


def generate_totp(secret: str) -> str:
    """Return the current TOTP code for a Base32 secret."""
    normalized = secret.replace(" ", "").replace("-", "").upper()
    return pyotp.TOTP(normalized).now()


def main() -> None:
    secret = getpass.getpass("Base32 secret (input hidden): ")
    try:
        print(generate_totp(secret))
    except Exception as exc:
        raise SystemExit(f"Invalid Base32 secret: {exc}") from exc


if __name__ == "__main__":
    main()
