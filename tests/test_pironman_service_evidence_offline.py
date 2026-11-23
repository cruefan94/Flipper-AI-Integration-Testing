"""Synthetic tests only: no Pi or Pironman access."""
import unittest
from pi_tools.pironman_service_evidence_offline import parse_service_snapshot


class ServiceEvidenceTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(parse_service_snapshot(""), ())

    def test_valid(self):
        result = parse_service_snapshot("pironman.service active\nother@1.service inactive")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].state, "active")
        self.assertFalse(result[0].confirmed)
        self.assertFalse(result[0].hardware_write_authorized)

    def test_reject_command(self):
        with self.assertRaises(ValueError):
            parse_service_snapshot("sudo systemctl restart pironman")

    def test_reject_unknown_state(self):
        with self.assertRaises(ValueError):
            parse_service_snapshot("pironman.service enabled")

    def test_reject_duplicate(self):
        with self.assertRaises(ValueError):
            parse_service_snapshot("a.service active\na.service failed")

    def test_reject_invalid_unit(self):
        with self.assertRaises(ValueError):
            parse_service_snapshot("../a.service active")

    def test_reject_oversize(self):
        with self.assertRaises(ValueError):
            parse_service_snapshot("a" * 16385)

    def test_reject_nonstring(self):
        with self.assertRaises(ValueError):
            parse_service_snapshot(None)


if __name__ == "__main__":
    unittest.main()
