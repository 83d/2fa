# Pure Python TOTP

A small, dependency-free implementation of:

- [RFC 4226](https://www.rfc-editor.org/rfc/rfc4226) — HOTP
- [RFC 6238](https://www.rfc-editor.org/rfc/rfc6238) — TOTP

It uses only Python's standard library and supports HMAC-SHA-1, SHA-256, and
SHA-512. The implementation includes generation, verification, a live CLI,
and the official RFC 6238 test vectors.

## Requirements

Python 3.9 or newer. No packages need to be installed.

## Command-line usage

The safest way to enter a secret is through the hidden prompt:

```console
python totp.py
Base32 secret (input hidden):
123456
```

Continuously display the code and its remaining lifetime:

```console
python totp.py --watch
```

Generate an eight-digit SHA-256 token for a specific Unix timestamp:

```console
python totp.py --algorithm SHA256 --digits 8 --timestamp 1234567890
```

Run `python totp.py --help` for all options.

## Python API

```python
from totp import generate_totp, remaining_seconds, verify_totp

secret = "JBSWY3DPEHPK3PXP"  # Public demonstration secret only.

token = generate_totp(secret)
print(token)
print(remaining_seconds(), "seconds remaining")

assert verify_totp(token, secret)
```

## Tests

```console
python -m unittest -v
```

The suite checks all SHA-1, SHA-256, and SHA-512 examples from Appendix B of
RFC 6238, plus input validation and clock-window behavior.

## Security notes

A TOTP secret is equivalent to the seed stored by an authenticator app.
Anyone who obtains it can generate the same codes.

- Do not put real secrets in URLs, Git repositories, logs, screenshots, or
  command history.
- Prefer the hidden prompt over the `--secret` option.
- Keep the system clock accurate.
- Server applications must protect stored secrets, use TLS, rate-limit
  verification attempts, and reject token reuse after successful validation.
- For important accounts, prefer a well-reviewed authenticator application
  or a phishing-resistant FIDO2/WebAuthn security key.

## License

[MIT](LICENSE)
