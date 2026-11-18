"""Public-safe adversarial regression tests for offline Pi/ESP32 identity observations.

No hardware discovery, ports, firmware, network calls, credentials or flashing.
These tests validate only the offline observation parser, not real USB identity.
"""
import copy
import unittest

from lab.pi_esp32_serial_identity_offline import inspect


def observation():
    return {
        "expected_chip": "esp32",
        "ports": [{
            "path": "/dev/serial/by-id/usb-Silicon_Labs_CP2102_TEST-if00-port0",
            "vid": "10c4",
            "pid": "ea60",
            "serial": "TEST1234",
            "chip": "esp32",
            "boot_mode": "download",
            "voltage_verified": True,
            "owner_authorized": True,
        }],
    }


class AdversarialOfflineTests(unittest.TestCase):
    def test_baseline_is_only_offline_ready(self):
        self.assertTrue(inspect(observation())["ready"])

    def test_non_mapping_input_rejected(self):
        for value in (None, [], "", 1):
            with self.subTest(value=value):
                self.assertFalse(inspect(value)["ready"])

    def test_invalid_port_records_rejected(self):
        for value in (None, "serial", [], 1):
            with self.subTest(value=value):
                data = observation()
                data["ports"] = [value]
                self.assertFalse(inspect(data)["ready"])

    def test_missing_usb_identifiers_rejected(self):
        for key in ("vid", "pid", "serial"):
            with self.subTest(key=key):
                data = observation()
                del data["ports"][0][key]
                self.assertFalse(inspect(data)["ready"])

    def test_invalid_usb_hex_rejected(self):
        for value in ("", "123", "12345", "zzzz", 1234):
            with self.subTest(value=value):
                data = observation()
                data["ports"][0]["vid"] = value
                self.assertFalse(inspect(data)["ready"])

    def test_path_traversal_and_tty_rejected(self):
        for path in ("/dev/ttyUSB0", "/dev/serial/by-id/../../ttyUSB0",
                     "/dev/serial/by-id/foo/bar", "/tmp/ttyUSB0"):
            with self.subTest(path=path):
                data = observation()
                data["ports"][0]["path"] = path
                self.assertFalse(inspect(data)["ready"])

    def test_truthy_strings_are_not_authorization(self):
        for key in ("owner_authorized", "voltage_verified"):
            for value in ("true", 1, None):
                with self.subTest(key=key, value=value):
                    data = observation()
                    data["ports"][0][key] = value
                    self.assertFalse(inspect(data)["ready"])

    def test_s2_mismatch_is_fail_closed(self):
        data = observation()
        data["expected_chip"] = "esp32s2"
        self.assertIn("CHIP_IDENTITY_UNCONFIRMED", inspect(data)["reasons"])

    def test_unknown_expected_chip_is_fail_closed(self):
        data = observation()
        data["expected_chip"] = "esp32c3"
        self.assertFalse(inspect(data)["ready"])

    def test_observation_is_not_mutated(self):
        data = observation()
        original = copy.deepcopy(data)
        inspect(data)
        self.assertEqual(data, original)


if __name__ == "__main__":
    unittest.main()
