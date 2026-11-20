#!/usr/bin/env python3
"""Offline ESP32/Pi serial inventory report. Never opens devices or invokes flashing tools.

Input: operator-supplied JSON with {"devices":[{"path":"/dev/ttyUSB0",
"usb_id":"10c4:ea60","board_hint":"unknown"}]}. Hints are untrusted.
"""
import argparse
import json
import re
import sys
import unittest

ALLOWED_PATH = re.compile(r"^/dev/tty(?:USB|ACM)[0-9]{1,3}$")
ALLOWED_USB = re.compile(r"^[0-9a-fA-F]{4}:[0-9a-fA-F]{4}$")
MAX_BYTES = 32768
MAX_DEVICES = 32


def report(raw):
    if not isinstance(raw, dict) or set(raw) != {"devices"}:
        raise ValueError("Expected only a devices array")
    devices = raw["devices"]
    if not isinstance(devices, list) or len(devices) > MAX_DEVICES:
        raise ValueError("Invalid device count")
    seen = set()
    output = []
    for entry in devices:
        if not isinstance(entry, dict) or set(entry) != {"path", "usb_id", "board_hint"}:
            raise ValueError("Invalid device record")
        path, usb_id, hint = (entry[k] for k in ("path", "usb_id", "board_hint"))
        if not isinstance(path, str) or not ALLOWED_PATH.fullmatch(path) or path in seen:
            raise ValueError("Invalid or duplicate serial path")
        if not isinstance(usb_id, str) or not ALLOWED_USB.fullmatch(usb_id):
            raise ValueError("Invalid USB VID:PID")
        if not isinstance(hint, str) or hint not in ("unknown", "esp32-wroom", "esp32-s2"):
            raise ValueError("Invalid unverified board hint")
        seen.add(path)
        output.append({"path": path, "usb_id": usb_id.lower(),
                       "board_hint_unverified": hint, "rom_identity": "NOT_VERIFIED",
                       "flash_authorized": False})
    return {"mode": "OFFLINE_READ_ONLY", "devices": output,
            "notice": "USB bridge ID and operator hint cannot establish ESP chip identity."}


class Tests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(report({"devices": []})["devices"], [])

    def test_valid(self):
        result = report({"devices": [{"path": "/dev/ttyUSB0", "usb_id": "10C4:EA60", "board_hint": "esp32-wroom"}]})
        self.assertFalse(result["devices"][0]["flash_authorized"])
        self.assertEqual(result["devices"][0]["rom_identity"], "NOT_VERIFIED")

    def test_duplicate(self):
        e = {"path": "/dev/ttyACM0", "usb_id": "303a:0002", "board_hint": "unknown"}
        with self.assertRaises(ValueError):
            report({"devices": [e, e]})

    def test_path_injection(self):
        with self.assertRaises(ValueError):
            report({"devices": [{"path": "/dev/ttyUSB0;erase_flash", "usb_id": "10c4:ea60", "board_hint": "unknown"}]})

    def test_extra_keys(self):
        with self.assertRaises(ValueError):
            report({"devices": [], "flash": True})

    def test_invalid_hint(self):
        with self.assertRaises(ValueError):
            report({"devices": [{"path": "/dev/ttyUSB1", "usb_id": "10c4:ea60", "board_hint": "confirmed"}]})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Offline JSON fixture file, never a device path")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    if not args.input or args.input.startswith("/dev/"):
        parser.error("--input must be an existing offline JSON fixture file")
    try:
        with open(args.input, "rb") as f:
            data = f.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("Input too large")
        print(json.dumps(report(json.loads(data.decode("utf-8"))), indent=2))
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print("INVALID OFFLINE INVENTORY: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
