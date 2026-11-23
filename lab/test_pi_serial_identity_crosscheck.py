"""Public-safe offline Pi/ESP32 serial-identity contract regressions."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("preflight", Path(__file__).with_name("pi_serial_identity_crosscheck.py"))
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)
BASE = {"label": "WROOM", "port": "/dev/ttyUSB0", "vid": "10c4", "pid": "ea60", "chip": "esp32"}

class IdentityContractTests(unittest.TestCase):
    def test_two_distinct_boards_never_authorize_flash(self):
        s2 = {"label": "S2", "port": "/dev/ttyACM1", "vid": "303a", "pid": "0002", "chip": "esp32-s2"}
        result = preflight.audit({"boards": [BASE, s2]})
        self.assertFalse(result["safe_to_flash"])
        self.assertFalse(result["hardware_accessed"])
        self.assertEqual(len(result["observations"]), 2)
        self.assertTrue(all(not b["verified_chip"] for b in result["observations"]))

    def test_same_usb_bridge_ids_do_not_imply_same_chip(self):
        other = dict(BASE, label="S2", port="/dev/ttyUSB1", chip="esp32-s2")
        result = preflight.audit({"boards": [BASE, other]})
        self.assertEqual(result["observations"][0]["usb_id"], result["observations"][1]["usb_id"])
        self.assertTrue(all(not b["verified_chip"] for b in result["observations"]))

    def test_unknown_chip_not_verified(self):
        result = preflight.audit({"boards": [dict(BASE, chip="unknown")]})
        self.assertFalse(result["observations"][0]["verified_chip"])

    def test_max_eight_boards(self):
        boards = [dict(BASE, label=f"B{i}", port=f"/dev/ttyUSB{i}") for i in range(8)]
        self.assertEqual(len(preflight.audit({"boards": boards})["observations"]), 8)
        with self.assertRaises(ValueError):
            preflight.audit({"boards": boards + [dict(BASE, label="B8", port="/dev/ttyUSB8")]})

    def test_non_string_fields_rejected(self):
        for key in ("label", "port", "vid", "pid", "chip"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                preflight.audit({"boards": [dict(BASE, **{key: None})]})

    def test_no_user_supplied_flash_authorization(self):
        with self.assertRaises(ValueError):
            preflight.audit({"boards": [BASE], "safe_to_flash": True})

    def test_case_insensitive_duplicate_labels(self):
        with self.assertRaises(ValueError):
            preflight.audit({"boards": [BASE, dict(BASE, label="wroom", port="/dev/ttyUSB1")]})

    def test_uppercase_usb_id_normalization(self):
        result = preflight.audit({"boards": [BASE]})
        self.assertEqual(result["observations"][0]["usb_id"], "10C4:EA60")

if __name__ == "__main__":
    unittest.main()
