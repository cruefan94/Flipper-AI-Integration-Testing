#!/usr/bin/env python3
"""Offline, public-safe USB inventory gate. No USB/serial access or flashing."""
import json
import re
import sys
import unittest

HEX4 = re.compile(r"^[0-9a-fA-F]{4}$")
SAFE_KIND = {"esp32_wroom_bridge", "esp32_s2", "arduino_uno", "flipper_zero", "unknown"}

def validate_inventory(records):
    if not isinstance(records, list) or len(records) > 16:
        raise ValueError("expected up to 16 synthetic USB records")
    result = []
    for item in records:
        if not isinstance(item, dict) or set(item) != {"vid", "pid", "kind"}:
            raise ValueError("only vid, pid and kind permitted; no serials or paths")
        vid, pid, kind = item["vid"], item["pid"], item["kind"]
        if not isinstance(vid, str) or not HEX4.fullmatch(vid):
            raise ValueError("invalid VID")
        if not isinstance(pid, str) or not HEX4.fullmatch(pid):
            raise ValueError("invalid PID")
        if kind not in SAFE_KIND:
            raise ValueError("unknown board class")
        result.append({"vid": vid.lower(), "pid": pid.lower(), "kind": kind,
                       "decision": "MANUAL_REVIEW_REQUIRED"})
    return result

class OfflineTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_inventory([{"vid":"10C4","pid":"EA60","kind":"esp32_wroom_bridge"}])[0]["decision"], "MANUAL_REVIEW_REQUIRED")
    def test_reject_serial(self):
        with self.assertRaises(ValueError):
            validate_inventory([{"vid":"10c4","pid":"ea60","kind":"unknown","serial":"SECRET"}])
    def test_reject_device_path(self):
        with self.assertRaises(ValueError):
            validate_inventory([{"vid":"10c4","pid":"ea60","kind":"unknown","path":"/dev/ttyUSB0"}])
    def test_reject_bad_hex(self):
        with self.assertRaises(ValueError):
            validate_inventory([{"vid":"xyz","pid":"ea60","kind":"unknown"}])
    def test_reject_unknown_kind(self):
        with self.assertRaises(ValueError):
            validate_inventory([{"vid":"10c4","pid":"ea60","kind":"modem"}])
    def test_reject_oversized(self):
        with self.assertRaises(ValueError):
            validate_inventory([{"vid":"0000","pid":"0000","kind":"unknown"}] * 17)

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        unittest.main(argv=[sys.argv[0]])
    else:
        print("Offline-only. Run --self-test; no USB probing or flashing implemented.")
