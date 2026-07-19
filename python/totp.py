#!/usr/bin/env python3
"""Dependency-free HOTP/TOTP generator and verifier.

Implements RFC 4226 (HOTP) and RFC 6238 (TOTP) with Python's standard
library. Run ``python totp.py --help`` for command-line usage.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import getpass
import hashlib
import hmac
import sys
import time
from collections.abc import Callable, Sequence
from typing import Final


HashFactory = Callable[..., "hashlib._Hash"]

_HASH_ALGORITHMS: Final[dict[str, HashFactory]] = {
    "SHA1": hashlib.sha1,
    "SHA256": hashlib.sha256,
    "SHA512": hashlib.sha512,
}


def decode_base32(secret: str) -> bytes:
    """Decode a Base32 secret, accepting spaces, hyphens, and omitted padding."""
    normalized = "".join(secret.split()).replace("-", "").upper()
    if not normalized:
        raise ValueError("the Base32 secret is empty")

    padding = "=" * ((8 - len(normalized) % 8) % 8)
    try:
        return base64.b32decode(normalized + padding, casefold=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("the secret is not valid Base32") from exc


def generate_hotp(
    secret: str,
    counter: int,
    *,
    digits: int = 6,
    algorithm: str = "SHA1",
) -> str:
    """Generate an RFC 4226 HOTP value."""
    if counter < 0:
        raise ValueError("counter must be non-negative")
    if not 6 <= digits <= 10:
        raise ValueError("digits must be between 6 and 10")

    algorithm = algorithm.upper().replace("-", "")
    try:
        digestmod = _HASH_ALGORITHMS[algorithm]
    except KeyError as exc:
        supported = ", ".join(_HASH_ALGORITHMS)
        raise ValueError(f"unsupported algorithm; choose one of: {supported}") from exc

    key = decode_base32(secret)
    message = counter.to_bytes(8, byteorder="big", signed=False)
    digest = hmac.new(key, message, digestmod).digest()

    offset = digest[-1] & 0x0F
    binary_code = int.from_bytes(digest[offset : offset + 4], "big") & 0x7FFFFFFF
    return str(binary_code % (10**digits)).zfill(digits)


def generate_totp(
    secret: str,
    *,
    timestamp: float | None = None,
    period: int = 30,
    digits: int = 6,
    algorithm: str = "SHA1",
) -> str:
    """Generate an RFC 6238 TOTP value for a Unix timestamp."""
    if period <= 0:
        raise ValueError("period must be positive")

    current_time = time.time() if timestamp is None else timestamp
    if current_time < 0:
        raise ValueError("timestamp must be non-negative")

    counter = int(current_time) // period
    return generate_hotp(
        secret,
        counter,
        digits=digits,
        algorithm=algorithm,
    )


def remaining_seconds(*, timestamp: float | None = None, period: int = 30) -> int:
    """Return the number of whole seconds until the current TOTP period ends."""
    if period <= 0:
        raise ValueError("period must be positive")

    current_time = time.time() if timestamp is None else timestamp
    if current_time < 0:
        raise ValueError("timestamp must be non-negative")
    return period - (int(current_time) % period)


def verify_totp(
    token: str,
    secret: str,
    *,
    timestamp: float | None = None,
    window: int = 0,
    period: int = 30,
    digits: int = 6,
    algorithm: str = "SHA1",
) -> bool:
    """Verify a TOTP token with an optional clock-drift window.

    ``window=1`` accepts the immediately preceding and following periods in
    addition to the current one. Server applications should also rate-limit
    attempts and reject reuse after a successful verification.
    """
    if window < 0:
        raise ValueError("window must be non-negative")
    if not token.isdigit() or len(token) != digits:
        return False

    current_time = time.time() if timestamp is None else timestamp
    for offset in range(-window, window + 1):
        candidate_time = current_time + offset * period
        if candidate_time < 0:
            continue
        candidate = generate_totp(
            secret,
            timestamp=candidate_time,
            period=period,
            digits=digits,
            algorithm=algorithm,
        )
        if hmac.compare_digest(token, candidate):
            return True
    return False


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate RFC 6238 TOTP codes without third-party packages."
    )
    parser.add_argument(
        "--secret",
        help=(
            "Base32 secret. Omitting this option uses a hidden prompt, which is "
            "safer because command arguments may be recorded."
        ),
    )
    parser.add_argument(
        "--algorithm",
        choices=tuple(_HASH_ALGORITHMS),
        default="SHA1",
        help="HMAC hash algorithm (default: SHA1)",
    )
    parser.add_argument(
        "--digits",
        type=int,
        default=6,
        help="number of output digits, 6-10 (default: 6)",
    )
    parser.add_argument(
        "--period",
        type=int,
        default=30,
        help="TOTP period in seconds (default: 30)",
    )
    parser.add_argument(
        "--timestamp",
        type=float,
        help="generate for a specific Unix timestamp instead of the current time",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="continuously display the current token and remaining time",
    )
    return parser


def _read_secret(argument: str | None) -> str:
    if argument is not None:
        return argument
    return getpass.getpass("Base32 secret (input hidden): ").strip()


def main(argv: Sequence[str] | None = None) -> int:
    """Command-line entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.watch and args.timestamp is not None:
        parser.error("--watch cannot be combined with --timestamp")

    secret = _read_secret(args.secret)
    try:
        if args.watch:
            while True:
                token = generate_totp(
                    secret,
                    period=args.period,
                    digits=args.digits,
                    algorithm=args.algorithm,
                )
                remaining = remaining_seconds(period=args.period)
                print(
                    f"\rTOTP: {token}  expires in {remaining:02d}s",
                    end="",
                    flush=True,
                )
                time.sleep(0.2)
        else:
            token = generate_totp(
                secret,
                timestamp=args.timestamp,
                period=args.period,
                digits=args.digits,
                algorithm=args.algorithm,
            )
            print(token)
    except KeyboardInterrupt:
        print()
        return 130
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
