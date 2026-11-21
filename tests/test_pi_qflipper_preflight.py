"""Offline tests: never inspect real PATH or USB devices."""
import unittest

from raspberry_pi.qflipper_preflight import preflight


class PreflightTests(unittest.TestCase):
    def test_no_consent_never_calls_lookup(self):
        def forbidden(_):
            raise AssertionError("lookup occurred")
        self.assertEqual(preflight(which=forbidden)["status"], "not_authorized")

    def test_found(self):
        result = preflight(consent=True, which=lambda name: "/mock/bin/qFlipper" if name == "qFlipper" else None)
        self.assertEqual(result["qflipper"], "available_on_path")
        self.assertEqual(result["usb"], "unknown")

    def test_missing(self):
        self.assertEqual(preflight(consent=True, which=lambda _: None)["qflipper"], "not_found_on_path")

    def test_lookup_error(self):
        def fail(_):
            raise OSError("mock")
        self.assertEqual(preflight(consent=True, which=fail)["qflipper"], "not_found_on_path")

    def test_invalid_consent(self):
        with self.assertRaises(ValueError):
            preflight(consent=1)

    def test_never_claims_recovery(self):
        for consent in (False, True):
            result = preflight(consent=consent, which=lambda _: "mock")
            self.assertEqual(result["backup"], "unknown")
            self.assertEqual(result["recovery"], "unknown")


if __name__ == "__main__":
    unittest.main()
