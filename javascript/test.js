"use strict";

const OTPAuth = require("./vendor/otpauth.umd.min.js");

const rfcSecret = OTPAuth.Secret.fromBase32(
  "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
);
const totp = new OTPAuth.TOTP({
  algorithm: "SHA1",
  digits: 8,
  period: 30,
  secret: rfcSecret,
});

const actual = totp.generate({ timestamp: 59_000 });
const expected = "94287082";

if (actual !== expected) {
  console.error(`RFC 6238 test failed: expected ${expected}, got ${actual}`);
  process.exit(1);
}

console.log(`RFC 6238 JavaScript test passed: ${actual}`);
