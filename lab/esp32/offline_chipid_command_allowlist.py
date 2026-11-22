#!/usr/bin/env python3
"""Offline-only ESP32 serial command plan validator. Never executes commands."""
import json
import re
import sys
import unittest

PORT = re.compile(r"^/dev/(ttyUSB[0-9]{1,3}|ttyACM[0-9]{1,3}|serial/by-id/[A-Za-z0-9_.-]{1,120})$")
CHIPS = {"esp32", "esp32s2", "esp32s3"}

def make_plan(spec):
    if not isinstance(spec, dict):
        raise ValueError("plan must be an object")
    if set(spec) != {"port", "chip", "uart_logic_v", "power_verified", "owner_consent"}:
        raise ValueError("exact five fields required")
    port, chip = spec["port"], spec["chip"]
    if not isinstance(port, str) or not PORT.fullmatch(port):
        raise ValueError("unapproved serial path")
    if type(chip) is not str or chip not in CHIPS:
        raise ValueError("unknown chip family")
    if type(spec["uart_logic_v"]) not in (int, float) or spec["uart_logic_v"] != 3.3:
        raise ValueError("3.3V UART logic must be confirmed")
    if spec["power_verified"] is not True or spec["owner_consent"] is not True:
        raise ValueError("power and owner consent required")
    # List of arguments, not a shell string. --no-stub avoids RAM stub upload.
    # This is a PLAN ONLY: no serial device is opened or reset.
    return {"mode": "offline-plan-only", "chip": chip,
            "argv": ["python3", "-m", "esptool", "--chip", chip,
                     "--port", port, "--no-stub", "chip_id"],
            "warning": "Do not execute until board/adapter schematic and reset behavior are verified."}

class Tests(unittest.TestCase):
    def setUp(self):
        self.valid = dict(port="/dev/ttyUSB0", chip="esp32", uart_logic_v=3.3,
                          power_verified=True, owner_consent=True)
    def test_valid(self):
        self.assertEqual(make_plan(self.valid)["mode"], "offline-plan-only")
    def test_s2(self):
        self.valid["chip"] = "esp32s2"
        self.assertEqual(make_plan(self.valid)["chip"], "esp32s2")
    def test_s3(self):
        self.valid["chip"] = "esp32s3"
        self.assertEqual(make_plan(self.valid)["chip"], "esp32s3")
    def test_serial_by_id(self):
        self.valid["port"] = "/dev/serial/by-id/usb-CP2102_123"
        self.assertEqual(make_plan(self.valid)["argv"][6], self.valid["port"])
    def test_injection(self):
        self.valid["port"] = "/dev/ttyUSB0;touch /tmp/x"
        with self.assertRaises(ValueError): make_plan(self.valid)
    def test_bad_chip(self):
        self.valid["chip"] = "auto"
        with self.assertRaises(ValueError): make_plan(self.valid)
    def test_five_volt(self):
        self.valid["uart_logic_v"] = 5
        with self.assertRaises(ValueError): make_plan(self.valid)
    def test_missing_consent(self):
        self.valid["owner_consent"] = False
        with self.assertRaises(ValueError): make_plan(self.valid)
    def test_missing_power(self):
        self.valid["power_verified"] = False
        with self.assertRaises(ValueError): make_plan(self.valid)
    def test_extra_key(self):
        self.valid["execute"] = True
        with self.assertRaises(ValueError): make_plan(self.valid)
    def test_bool_voltage(self):
        self.valid["uart_logic_v"] = True
        with self.assertRaises(ValueError): make_plan(self.valid)

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        unittest.main(argv=[sys.argv[0]])
    else:
        print("Offline planner only. Run --self-test; import make_plan(dict) to create a plan.")
