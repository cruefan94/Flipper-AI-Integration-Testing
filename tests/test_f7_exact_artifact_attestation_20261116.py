"""Public-safe, synthetic-only F7 updater evidence acceptance tests.

This module never downloads, decrypts, or publishes firmware artifacts.
The manifest is an attestation *summary*, not proof of hardware success.
"""
import re
import unittest

HEX256 = re.compile(r"[0-9a-f]{64}\Z")
HEX32 = re.compile(r"[0-9a-f]{8}\Z")
ALLOWED = {
    "source_repository", "source_sha", "workflow_run_id", "encrypted_artifact_id",
    "encrypted_zip_sha256", "native_tgz_sha256", "firmware_dfu_sha256",
    "dfu_suffix_crc32", "dfu_suffix_crc_verified", "native_archive_verified",
    "encrypted_only_public_artifact", "verification_location",
}


def validate_attestation(record):
    """Reject incomplete or ambiguous evidence; do not treat a green job as CRC proof."""
    if not isinstance(record, dict) or set(record) != ALLOWED:
        return False
    if record["source_repository"] != "cruefan94/Flipper-AI-Momentum-":
        return False
    if not isinstance(record["source_sha"], str) or not HEX256.fullmatch(record["source_sha"].lower()):
        return False
    for key in ("workflow_run_id", "encrypted_artifact_id"):
        if type(record[key]) is not int or record[key] <= 0:
            return False
    for key in ("encrypted_zip_sha256", "native_tgz_sha256", "firmware_dfu_sha256"):
        if not isinstance(record[key], str) or not HEX256.fullmatch(record[key]):
            return False
    if len({record[k] for k in ("encrypted_zip_sha256", "native_tgz_sha256", "firmware_dfu_sha256")}) != 3:
        return False
    if not isinstance(record["dfu_suffix_crc32"], str) or not HEX32.fullmatch(record["dfu_suffix_crc32"]):
        return False
    if any(record[k] is not True for k in
           ("dfu_suffix_crc_verified", "native_archive_verified", "encrypted_only_public_artifact")):
        return False
    return record["verification_location"] == "private-runner"


class F7AttestationTests(unittest.TestCase):
    def setUp(self):
        self.good = {
            "source_repository": "cruefan94/Flipper-AI-Momentum-",
            "source_sha": "a" * 64,
            "workflow_run_id": 12345,
            "encrypted_artifact_id": 67890,
            "encrypted_zip_sha256": "b" * 64,
            "native_tgz_sha256": "c" * 64,
            "firmware_dfu_sha256": "d" * 64,
            "dfu_suffix_crc32": "1234abcd",
            "dfu_suffix_crc_verified": True,
            "native_archive_verified": True,
            "encrypted_only_public_artifact": True,
            "verification_location": "private-runner",
        }

    def test_complete_synthetic_attestation(self):
        self.assertTrue(validate_attestation(self.good))

    def test_green_job_without_real_crc_proof_rejected(self):
        self.assertFalse(validate_attestation({**self.good, "dfu_suffix_crc_verified": False}))

    def test_encrypted_zip_hash_cannot_substitute_native_hash(self):
        self.assertFalse(validate_attestation({**self.good, "native_tgz_sha256": "b" * 64}))

    def test_missing_native_hash_rejected(self):
        candidate = dict(self.good)
        del candidate["native_tgz_sha256"]
        self.assertFalse(validate_attestation(candidate))

    def test_private_source_or_token_fields_rejected(self):
        self.assertFalse(validate_attestation({**self.good, "private_token": "secret"}))

    def test_wrong_source_repository_rejected(self):
        self.assertFalse(validate_attestation({**self.good, "source_repository": "other/repo"}))

    def test_unverified_native_archive_rejected(self):
        self.assertFalse(validate_attestation({**self.good, "native_archive_verified": False}))

    def test_unencrypted_public_artifact_rejected(self):
        self.assertFalse(validate_attestation({**self.good, "encrypted_only_public_artifact": False}))

    def test_public_runner_claim_of_private_verification_rejected(self):
        self.assertFalse(validate_attestation({**self.good, "verification_location": "public-runner"}))

    def test_bad_crc_and_sha_rejected(self):
        self.assertFalse(validate_attestation({**self.good, "dfu_suffix_crc32": "not-a-crc"}))
        self.assertFalse(validate_attestation({**self.good, "firmware_dfu_sha256": "unknown"}))

    def test_boolean_run_id_rejected(self):
        self.assertFalse(validate_attestation({**self.good, "workflow_run_id": True}))


if __name__ == "__main__":
    unittest.main()
