"""Offline receive-only USB SDR plan policy. No hardware, network or radio access."""
import math
import unittest

def validate(p):
    if not isinstance(p, dict):
        return ["plan must be an object"]
    errors = []
    required = {"operation": "receive_only", "transmit_enabled": False,
                "device_access": False, "recording_enabled": False,
                "encrypted_or_private": False, "source": "usb_sdr",
                "public_or_authorized": True, "country": "CA",
                "remote_control_url": None}
    for key, expected in required.items():
        if key not in p or type(p[key]) is not type(expected) or p[key] != expected:
            errors.append("invalid or missing " + key)
    if p.get("mode") not in ("WFM", "AM", "NFM"):
        errors.append("unsupported demodulation mode")
    for key, low, high in (("frequency_mhz", 0.1, 1800), ("gain_db", 0, 50)):
        value = p.get(key)
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            errors.append("invalid " + key)
    return errors

class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.p = dict(operation="receive_only", transmit_enabled=False,
                      device_access=False, recording_enabled=False,
                      encrypted_or_private=False, source="usb_sdr", mode="WFM",
                      frequency_mhz=99.9, gain_db=20,
                      public_or_authorized=True, country="CA",
                      remote_control_url=None)
    def test_valid(self):
        self.assertEqual(validate(self.p), [])
    def test_not_dict(self):
        self.assertTrue(validate(None))
    def test_invalid_fields(self):
        cases = [
            ("operation", "transmit"), ("transmit_enabled", True),
            ("device_access", True), ("recording_enabled", True),
            ("encrypted_or_private", True), ("source", "network"),
            ("mode", "TX"), ("frequency_mhz", float("nan")),
            ("frequency_mhz", True), ("gain_db", float("inf")),
            ("gain_db", -1), ("public_or_authorized", False),
            ("country", "US"), ("remote_control_url", "https://example.org"),
        ]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                candidate = self.p.copy()
                candidate[key] = value
                self.assertTrue(validate(candidate))
    def test_missing_fields(self):
        for key in self.p:
            with self.subTest(key=key):
                candidate = self.p.copy()
                del candidate[key]
                self.assertTrue(validate(candidate))

if __name__ == "__main__":
    unittest.main()
