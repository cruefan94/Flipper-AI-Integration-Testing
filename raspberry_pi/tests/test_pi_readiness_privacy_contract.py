"""Synthetic privacy and fail-closed contract for the Pi-only backup readiness UI.

No hardware, backup files, privileged commands, or restore operations.
"""
import unittest

from raspberry_pi.pi_backup_readiness import summarize_readiness


class ReadinessPrivacyContractTests(unittest.TestCase):
    def test_private_fields_never_propagate(self):
        secret = "PRIVATE_SENTINEL_DO_NOT_RENDER"
        source = {
            "ok": True, "read_only": True, "identity_verified": False,
            "path": secret, "sha256": secret, "device_serial": secret,
            "results": [{"status": "ok", "path": secret, "sha256": secret}],
        }
        summary = summarize_readiness(source)
        self.assertEqual(summary["status"], "integrity_checked")
        self.assertNotIn(secret, repr(summary))
        self.assertEqual(set(summary), {
            "ready_for_manual_review", "verified_files", "total_files",
            "failed_files", "identity_verified", "restore_authorized", "status",
        })
        self.assertFalse(summary["restore_authorized"])

    def test_untrusted_restore_and_identity_flags_cannot_authorize(self):
        source = {
            "ok": True, "read_only": True, "identity_verified": True,
            "restore_authorized": True, "ready_for_manual_review": True,
            "results": [{"status": "ok"}],
        }
        summary = summarize_readiness(source)
        self.assertFalse(summary["ready_for_manual_review"])
        self.assertFalse(summary["identity_verified"])
        self.assertFalse(summary["restore_authorized"])

    def test_mixed_result_never_ready_even_when_top_level_ok(self):
        summary = summarize_readiness({
            "ok": True, "read_only": True, "identity_verified": False,
            "results": [{"status": "ok"}, {"status": "mismatch"}],
        })
        self.assertEqual(summary["verified_files"], 1)
        self.assertEqual(summary["failed_files"], 1)
        self.assertFalse(summary["ready_for_manual_review"])
        self.assertFalse(summary["restore_authorized"])

    def test_malformed_statuses_fail_closed_without_echo(self):
        for status in ([], {}, None, True, 1):
            with self.subTest(kind=type(status).__name__):
                summary = summarize_readiness({
                    "ok": True, "read_only": True, "identity_verified": False,
                    "results": [{"status": status, "path": "PRIVATE_SENTINEL_DO_NOT_RENDER"}],
                })
                self.assertEqual(summary["status"], "invalid_verification")
                self.assertFalse(summary["restore_authorized"])
                self.assertNotIn("PRIVATE_SENTINEL", repr(summary))


if __name__ == "__main__":
    unittest.main()
