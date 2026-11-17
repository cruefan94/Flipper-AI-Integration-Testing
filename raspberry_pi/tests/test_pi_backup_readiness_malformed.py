"""Synthetic malformed-status contract for privacy-safe backup readiness."""
import unittest

from raspberry_pi.pi_backup_readiness import summarize_readiness


class MalformedStatusTests(unittest.TestCase):
    def test_unhashable_statuses_fail_closed_without_exception(self):
        for status in ([], {}, ["ok"], {"status": "ok"}):
            with self.subTest(status_type=type(status).__name__):
                result = summarize_readiness({
                    "ok": True, "read_only": True, "identity_verified": False,
                    "results": [{"status": status}],
                })
                self.assertEqual(result["status"], "invalid_verification")
                self.assertFalse(result["ready_for_manual_review"])
                self.assertFalse(result["restore_authorized"])

    def test_non_string_hashable_statuses_fail_closed(self):
        for status in (None, 0, True, ("ok",)):
            with self.subTest(status_type=type(status).__name__):
                result = summarize_readiness({
                    "ok": True, "read_only": True, "identity_verified": False,
                    "results": [{"status": status}],
                })
                self.assertEqual(result["status"], "invalid_verification")
                self.assertFalse(result["restore_authorized"])

    def test_known_status_preserves_read_only_review(self):
        result = summarize_readiness({
            "ok": True, "read_only": True, "identity_verified": False,
            "results": [{"status": "ok"}],
        })
        self.assertEqual(result["status"], "integrity_checked")
        self.assertTrue(result["ready_for_manual_review"])
        self.assertFalse(result["restore_authorized"])


if __name__ == "__main__":
    unittest.main()
