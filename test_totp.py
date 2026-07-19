"""RFC test vectors and behavior tests for totp.py."""

import base64
import unittest

from totp import (
    decode_base32,
    generate_hotp,
    generate_totp,
    remaining_seconds,
    verify_totp,
)


def as_base32(value: bytes) -> str:
    return base64.b32encode(value).decode("ascii").rstrip("=")


class RFC6238Tests(unittest.TestCase):
    SHA1_SECRET = as_base32(b"12345678901234567890")
    SHA256_SECRET = as_base32(b"12345678901234567890123456789012")
    SHA512_SECRET = as_base32(
        b"1234567890123456789012345678901234567890123456789012345678901234"
    )

    VECTORS = (
        (59, "94287082", "46119246", "90693936"),
        (1_111_111_109, "07081804", "68084774", "25091201"),
        (1_111_111_111, "14050471", "67062674", "99943326"),
        (1_234_567_890, "89005924", "91819424", "93441116"),
        (2_000_000_000, "69279037", "90698825", "38618901"),
        (20_000_000_000, "65353130", "77737706", "47863826"),
    )

    def test_rfc_6238_vectors(self) -> None:
        for timestamp, sha1, sha256, sha512 in self.VECTORS:
            with self.subTest(timestamp=timestamp, algorithm="SHA1"):
                self.assertEqual(
                    generate_totp(
                        self.SHA1_SECRET,
                        timestamp=timestamp,
                        digits=8,
                        algorithm="SHA1",
                    ),
                    sha1,
                )
            with self.subTest(timestamp=timestamp, algorithm="SHA256"):
                self.assertEqual(
                    generate_totp(
                        self.SHA256_SECRET,
                        timestamp=timestamp,
                        digits=8,
                        algorithm="SHA256",
                    ),
                    sha256,
                )
            with self.subTest(timestamp=timestamp, algorithm="SHA512"):
                self.assertEqual(
                    generate_totp(
                        self.SHA512_SECRET,
                        timestamp=timestamp,
                        digits=8,
                        algorithm="SHA512",
                    ),
                    sha512,
                )


class BehaviorTests(unittest.TestCase):
    SECRET = "JBSWY3DPEHPK3PXP"

    def test_base32_normalization(self) -> None:
        self.assertEqual(
            decode_base32("jbsw y3dp-ehpk3pxp"),
            decode_base32(self.SECRET),
        )

    def test_hotp_is_six_digits_by_default(self) -> None:
        self.assertRegex(generate_hotp(self.SECRET, 0), r"^\d{6}$")

    def test_verification_window(self) -> None:
        token = generate_totp(self.SECRET, timestamp=59)
        self.assertTrue(verify_totp(token, self.SECRET, timestamp=59))
        self.assertFalse(verify_totp(token, self.SECRET, timestamp=60))
        self.assertTrue(verify_totp(token, self.SECRET, timestamp=60, window=1))

    def test_remaining_seconds(self) -> None:
        self.assertEqual(remaining_seconds(timestamp=0), 30)
        self.assertEqual(remaining_seconds(timestamp=29), 1)
        self.assertEqual(remaining_seconds(timestamp=30), 30)

    def test_invalid_input(self) -> None:
        with self.assertRaises(ValueError):
            decode_base32("not-valid-1")
        with self.assertRaises(ValueError):
            generate_hotp(self.SECRET, -1)
        with self.assertRaises(ValueError):
            generate_totp(self.SECRET, period=0)
        with self.assertRaises(ValueError):
            generate_totp(self.SECRET, digits=5)
        with self.assertRaises(ValueError):
            generate_totp(self.SECRET, algorithm="MD5")


if __name__ == "__main__":
    unittest.main()
