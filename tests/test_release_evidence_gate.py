"""Synthetic, public-safe tests: no actual firmware, fingerprints, or private logs."""
import unittest
from tools.release_evidence_gate import validate

BASE = {
    "source_commit": "a" * 40,
    "ci_run_url": "https://github.com/example/safe/actions/runs/123",
    "artifact_sha256": "b" * 64,
    "artifact_kind": "f7-native-tgz",
    "real_artifact_crc_verified": True,
    "recovery_verified": True,
    "hardware_verified": True,
}

class ReleaseEvidenceTests(unittest.TestCase):
    def test_valid_synthetic_f7_only_manual_review(self):
        self.assertEqual(validate(BASE), [])
    def test_missing_provenance(self):
        self.assertTrue(validate({}))
    def test_wrong_artifact(self):
        self.assertTrue(validate({**BASE, "artifact_kind": "esp32-encrypted"}))
    def test_crc_gate(self):
        self.assertIn("F7 real-artifact DFU CRC evidence missing",
                      validate({**BASE, "real_artifact_crc_verified": False}))
    def test_no_hardware_proof(self):
        self.assertTrue(validate({**BASE, "hardware_verified": False}))
    def test_no_recovery(self):
        self.assertTrue(validate({**BASE, "recovery_verified": False}))
    def test_bad_sha(self):
        self.assertTrue(validate({**BASE, "source_commit": "short"}))
    def test_bad_url(self):
        self.assertTrue(validate({**BASE, "ci_run_url": "https://other.test/123"}))
    def test_android_requires_signing_and_version(self):
        self.assertTrue(validate({**BASE, "artifact_kind": "android-test-apk"}))
    def test_android_synthetic_eligible(self):
        m = {**BASE, "artifact_kind": "android-test-apk",
             "signing_compatible": True, "version_code_increases": True}
        self.assertEqual(validate(m), [])

if __name__ == "__main__":
    unittest.main()
