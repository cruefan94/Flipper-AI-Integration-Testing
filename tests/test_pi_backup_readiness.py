"""Synthetic, no-hardware tests for the read-only readiness summary."""
import unittest

from raspberry_pi.pi_backup_readiness import summarize_readiness


class ReadinessTests(unittest.TestCase):
    def test_valid_verified_files_are_review_only(self):
        report = summarize_readiness({
            "ok": True, "read_only": True, "identity_verified": False,
            "results": [{"status": "ok"}, {"status": "ok"}],
        })
        self.assertTrue(report["ready_for_manual_review"])
        self.assertFalse(report["restore_authorized"])
        self.assertFalse(report["identity_verified"])
        self.assertEqual(report["verified_files"], 2)

    def test_mismatch_is_not_ready(self):
        report = summarize_readiness({
            "ok": False, "read_only": True, "identity_verified": False,
            "results": [{"status": "ok"}, {"status": "mismatch"}],
        })
        self.assertFalse(report["ready_for_manual_review"])
        self.assertEqual(report["failed_files"], 1)

    def test_empty_and_malformed_fail_closed(self):
        for value in (None, {}, {"results": []}, {"results": [{"status": "surprise"}]}):
            with self.subTest(value=value):
                self.assertEqual(summarize_readiness(value)["status"], "invalid_verification")

    def test_no_filename_or_hash_leak(self):
        secret = "/home/private/sensitive-backup.bin"
        report = summarize_readiness({
            "ok": False, "read_only": True, "identity_verified": False,
            "results": [{"status": "read_error", "path": secret, "sha256": "deadbeef"}],
            "backup_root": secret,
        })
        self.assertNotIn(secret, str(report))
        self.assertNotIn("deadbeef", str(report))

    def test_cannot_claim_verified_identity_or_write_access(self):
        for key, value in (("identity_verified", True), ("read_only", False)):
            source = {"ok": True, "read_only": True, "identity_verified": False,
                      "results": [{"status": "ok"}]}
            source[key] = value
            with self.subTest(key=key):
                self.assertFalse(summarize_readiness(source)["ready_for_manual_review"])


if __name__ == "__main__":
    unittest.main()
