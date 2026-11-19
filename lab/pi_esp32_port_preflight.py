#!/usr/bin/env python3
"""Offline, fail-closed Raspberry Pi ESP32 serial preflight. No device I/O.

Usage: python3 pi_esp32_port_preflight.py --self-test
       python3 pi_esp32_port_preflight.py manifest.json
Manifest fields: chip, port, baud, voltage_verified, ground_verified,
                 manual_boot_verified, owner_authorized, operation
This tool never opens a serial port or invokes esptool.
"""
import argparse
import json
import re
import sys
import unittest

CHIPS = {"esp32", "esp32-s2"}
BAUD = {9600, 115200, 230400, 460800}
PORT = re.compile(r"^/dev/(ttyUSB[0-9]{1,2}|ttyACM[0-9]{1,2})$")
REQUIRED = {"chip", "port", "baud", "voltage_verified", "ground_verified",
            "manual_boot_verified", "owner_authorized", "operation"}

def validate(manifest):
    errors = []
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]
    if set(manifest) != REQUIRED:
        errors.append("manifest keys must match the documented schema")
    if manifest.get("chip") not in CHIPS:
        errors.append("unsupported ESP32 chip family")
    port = manifest.get("port")
    if not isinstance(port, str) or not PORT.fullmatch(port):
        errors.append("port must be a local ttyUSB/ttyACM device path")
    baud = manifest.get("baud")
    if type(baud) is not int or baud not in BAUD:
        errors.append("unsupported serial baud rate")
    if manifest.get("operation") != "read_only_preflight":
        errors.append("only read_only_preflight is permitted")
    for field in ("voltage_verified", "ground_verified",
                  "manual_boot_verified", "owner_authorized"):
        if manifest.get(field) is not True:
            errors.append(field + " must be explicitly true")
    return errors

class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.good = dict(chip="esp32", port="/dev/ttyUSB0", baud=115200,
                         voltage_verified=True, ground_verified=True,
                         manual_boot_verified=True, owner_authorized=True,
                         operation="read_only_preflight")
    def test_valid_wroom(self):
        self.assertEqual(validate(self.good), [])
    def test_valid_s2(self):
        self.good["chip"] = "esp32-s2"
        self.assertEqual(validate(self.good), [])
    def test_wrong_chip(self):
        self.good["chip"] = "esp8266"
        self.assertTrue(validate(self.good))
    def test_nonlocal_port(self):
        self.good["port"] = "socket://remote:1234"
        self.assertTrue(validate(self.good))
    def test_path_traversal(self):
        self.good["port"] = "/dev/ttyUSB0/../../mem"
        self.assertTrue(validate(self.good))
    def test_flash_operation(self):
        self.good["operation"] = "flash"
        self.assertTrue(validate(self.good))
    def test_boolean_baud(self):
        self.good["baud"] = True
        self.assertTrue(validate(self.good))
    def test_missing_authorization(self):
        self.good["owner_authorized"] = False
        self.assertTrue(validate(self.good))
    def test_missing_ground(self):
        self.good["ground_verified"] = False
        self.assertTrue(validate(self.good))
    def test_extra_field(self):
        self.good["command"] = "erase_flash"
        self.assertTrue(validate(self.good))
    def test_nonobject(self):
        self.assertTrue(validate([]))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(PreflightTests)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    if not args.manifest:
        parser.error("provide a manifest or --self-test")
    try:
        with open(args.manifest, encoding="utf-8") as handle:
            manifest = json.load(handle)
    except (OSError, ValueError) as exc:
        print("BLOCKED: invalid manifest: " + str(exc), file=sys.stderr)
        return 2
    errors = validate(manifest)
    if errors:
        print("BLOCKED: " + "; ".join(errors))
        return 1
    print("PASS: offline manifest preflight only; hardware and ROM handshake NOT verified")
    return 0

if __name__ == "__main__":
    sys.exit(main())
