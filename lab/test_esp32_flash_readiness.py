"""Public-safe synthetic tests: no serial, radio, hardware or firmware access."""
import unittest
from esp32_flash_readiness import evaluate

BASE = {"chip": "esp32", "port": "/dev/ttyUSB0", "boot_log": "DOWNLOAD_BOOT", "wiring_checked": True, "owner_authorized": True}

class ReadinessTests(unittest.TestCase):
    def test_advisory_only(self):
        self.assertEqual(evaluate(BASE)["reason"], "physical-verification-required")
        self.assertFalse(evaluate(BASE)["ready"])
    def test_s2(self):
        self.assertFalse(evaluate({**BASE, "chip": "esp32-s2"})["ready"])
    def test_unknown_chip(self):
        self.assertEqual(evaluate({**BASE, "chip": "esp32-c3"})["reason"], "unknown-chip")
    def test_invalid_port(self):
        self.assertEqual(evaluate({**BASE, "port": "COM03"})["reason"], "invalid-port")
    def test_no_authorization(self):
        self.assertEqual(evaluate({**BASE, "owner_authorized": False})["reason"], "missing-safety-confirmation")
    def test_no_wiring_check(self):
        self.assertFalse(evaluate({**BASE, "wiring_checked": False})["ready"])
    def test_unknown_fields(self):
        self.assertEqual(evaluate({**BASE, "flash": True})["reason"], "invalid-schema")
    def test_oversized_log(self):
        self.assertEqual(evaluate({**BASE, "boot_log": "x"*4097})["reason"], "invalid-log")
    def test_no_bypass(self):
        for value in (1, "true", None):
            self.assertFalse(evaluate({**BASE, "owner_authorized": value})["ready"])

if __name__ == "__main__":
    unittest.main()
