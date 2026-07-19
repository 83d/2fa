# TOTP Toolkit

Simple [RFC 6238 TOTP](https://www.rfc-editor.org/rfc/rfc6238) examples for
both Python and browser JavaScript.

The Python script uses the open-source [PyOTP](https://github.com/pyauth/pyotp)
package. The JavaScript version is a static local-first web page powered by the
vendored open-source [OTPAuth](https://github.com/hectorm/otpauth) library.
Neither version needs a backend service to generate codes.

## Repository layout

```text
totp-toolkit/
├── python/
│   └── totp.py              # Small PyOTP-based command-line generator
├── requirements.txt         # Pinned Python dependency
└── javascript/
    ├── index.html           # Offline browser interface
    ├── test.js              # RFC 6238 JavaScript smoke test
    └── vendor/
        ├── otpauth.umd.min.js
        └── LICENSE-*        # Third-party license texts
```

## Python version

Install PyOTP and run the script:

```console
python -m pip install -r requirements.txt
python python/totp.py
```

The secret is entered through a hidden prompt so it does not appear in command
history. The underlying Python operation is simply:

```python
import pyotp

print(pyotp.TOTP("JBSWY3DPEHPK3PXP").now())
```

## JavaScript version

Open `javascript/index.html` directly in a browser. It loads OTPAuth from the
local `javascript/vendor` directory, performs the calculation in the browser,
does not make external network requests, and does not store the secret in
localStorage or cookies.

The page includes:

- Base32 secret validation
- Automatic 30-second refresh and countdown
- One-click token copying
- A public demonstration secret
- A local Content Security Policy that blocks network connections

An RFC 6238 smoke test can also be run with Node.js:

```console
node javascript/test.js
```

For production distribution, keep the vendored script local and review any
dependency update before replacing it.

## Security notes

A TOTP secret is equivalent to the seed stored by an authenticator app.
Anyone who obtains it can generate the same codes.

- Do not put real secrets in URLs, Git repositories, logs, screenshots, or
  command history.
- Keep the system clock accurate.
- Do not add analytics, advertising, or other remote scripts to the web page.
- Server applications must protect stored secrets, use TLS, rate-limit
  verification attempts, and reject token reuse after successful validation.
- For important accounts, prefer a well-reviewed authenticator application
  or a phishing-resistant FIDO2/WebAuthn security key.

## Third-party software

The JavaScript page includes OTPAuth 9.4.0 and its bundled noble-hashes 1.7.1
dependency. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and the license
files in `javascript/vendor`.

## License

Project-authored code is released under the [MIT License](LICENSE). Vendored
dependencies retain their respective licenses.
