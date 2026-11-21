#!/usr/bin/env python3
"""OFFLINE ESP32 flash command preflight. Never opens serial ports or runs esptool.

Only renders a proposed read-only chip-identification command for owner review.
No flash/erase/reset operations are implemented. Public-safe synthetic tests.
"""
import argparse
import json
import re
import unittest

PORT = re.compile(r"^/dev/(ttyUSB|ttyACM)[0-9]{1,3}$")
CHIPS = {"esp32", "esp32s2"}

def plan(chip, port, owner_approved=False):
    if chip not in CHIPS:
        raise ValueError("unsupported chip; ESP32-S2 is not classic ESP32")
    if not isinstance(port, str) or not PORT.fullmatch(port):
        raise ValueError("invalid Pi serial port path")
    if owner_approved is not True:
        raise ValueError("explicit owner approval required even for chip-id probing")
    return {"mode": "PLAN_ONLY", "executes": False, "chip": chip,
            "argv": ["python3", "-m", "esptool", "--chip", chip,
                     "--port", port, "chip_id"],
            "warnings": ["Verify USB VID/PID and exact board first",
                         "Disconnect Flipper/Arduino GPIO wiring before USB diagnostics",
                         "3.3V logic only; never connect 5V UART to ESP32",
                         "No flash, erase, reset or serial I/O is performed here"]}

class OfflineTests(unittest.TestCase):
    def test_classic(self):
        self.assertEqual(plan("esp32", "/dev/ttyUSB0", True)["mode"], "PLAN_ONLY")
    def test_s2(self):
        self.assertEqual(plan("esp32s2", "/dev/ttyACM1", True)["chip"], "esp32s2")
    def test_no_approval(self):
        with self.assertRaises(ValueError): plan("esp32", "/dev/ttyUSB0")
    def test_bad_chip(self):
        with self.assertRaises(ValueError): plan("esp32s3", "/dev/ttyUSB0", True)
    def test_shell_injection(self):
        with self.assertRaises(ValueError): plan("esp32", "/dev/ttyUSB0;echo hi", True)
    def test_other_device(self):
        with self.assertRaises(ValueError): plan("esp32", "/dev/serial/by-id/example", True)
    def test_empty_port(self):
        with self.assertRaises(ValueError): plan("esp32", "", True)
    def test_no_write_command(self):
        self.assertNotIn("write_flash", plan("esp32", "/dev/ttyUSB2", True)["argv"])
    def test_approval_must_be_boolean(self):
        with self.assertRaises(ValueError): plan("esp32", "/dev/ttyUSB0", 1)
    def test_no_execution(self):
        self.assertIs(plan("esp32", "/dev/ttyUSB0", True)["executes"], False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--chip", choices=sorted(CHIPS))
    parser.add_argument("--port")
    parser.add_argument("--owner-approved", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["offline_tests"], exit=False)
    else:
        try:
            print(json.dumps(plan(args.chip, args.port, args.owner_approved), indent=2))
        except ValueError as exc:
            parser.error(str(exc))
