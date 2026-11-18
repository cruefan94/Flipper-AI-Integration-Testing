#!/usr/bin/env python3
"""Offline Raspberry Pi ESP32 serial identity preflight. Never opens a device.

Input: JSON file containing expected_chip, ports (array of observations).
No USB discovery, serial operations, subprocesses, GPIO, erase or flashing.
"""
import argparse
import json
import re
import sys
import unittest

CHIPS = {"esp32", "esp32s2"}
BY_ID = re.compile(r"^/dev/serial/by-id/[A-Za-z0-9_.:+-]+$")
HEX4 = re.compile(r"^[0-9a-fA-F]{4}$")
SERIAL = re.compile(r"^[A-Za-z0-9_.-]{4,128}$")


def inspect(data):
    """Return sanitized, fail-closed result from untrusted offline observations."""
    if not isinstance(data, dict) or data.get("expected_chip") not in CHIPS:
        return {"ready": False, "reasons": ["UNKNOWN_EXPECTED_CHIP"]}
    ports = data.get("ports")
    if not isinstance(ports, list) or len(ports) != 1:
        return {"ready": False, "reasons": ["REQUIRE_EXACTLY_ONE_PORT"]}
    p = ports[0]
    if not isinstance(p, dict):
        return {"ready": False, "reasons": ["INVALID_PORT_RECORD"]}
    reasons = []
    if not isinstance(p.get("path"), str) or not BY_ID.fullmatch(p["path"]):
        reasons.append("UNSTABLE_OR_UNSAFE_PATH")
    if not all(isinstance(p.get(k), str) and HEX4.fullmatch(p[k]) for k in ("vid", "pid")):
        reasons.append("INVALID_USB_ID")
    if not isinstance(p.get("serial"), str) or not SERIAL.fullmatch(p["serial"]):
        reasons.append("MISSING_UNIQUE_SERIAL")
    if p.get("chip") != data["expected_chip"]:
        reasons.append("CHIP_IDENTITY_UNCONFIRMED")
    if p.get("boot_mode") != "download":
        reasons.append("ROM_DOWNLOAD_MODE_UNCONFIRMED")
    if p.get("voltage_verified") is not True:
        reasons.append("VOLTAGE_UNVERIFIED")
    if p.get("owner_authorized") is not True:
        reasons.append("OWNER_AUTHORIZATION_MISSING")
    return {"ready": not reasons, "reasons": reasons}


class OfflineTests(unittest.TestCase):
    def fixture(self):
        return {"expected_chip": "esp32", "ports": [{
            "path": "/dev/serial/by-id/usb-Silicon_Labs_CP2102_ABC-if00-port0",
            "vid": "10c4", "pid": "ea60", "serial": "ABC12345",
            "chip": "esp32", "boot_mode": "download",
            "voltage_verified": True, "owner_authorized": True
        }]}

    def test_valid_offline_observation(self):
        self.assertTrue(inspect(self.fixture())["ready"])

    def test_ambiguous_ports(self):
        d = self.fixture()
        d["ports"].append(dict(d["ports"][0]))
        self.assertEqual(inspect(d)["reasons"], ["REQUIRE_EXACTLY_ONE_PORT"])

    def test_unstable_tty_path(self):
        d = self.fixture()
        d["ports"][0]["path"] = "/dev/ttyUSB0"
        self.assertIn("UNSTABLE_OR_UNSAFE_PATH", inspect(d)["reasons"])

    def test_chip_mismatch(self):
        d = self.fixture()
        d["ports"][0]["chip"] = "esp32s2"
        self.assertIn("CHIP_IDENTITY_UNCONFIRMED", inspect(d)["reasons"])

    def test_s2_matching(self):
        d = self.fixture()
        d["expected_chip"] = "esp32s2"
        d["ports"][0]["chip"] = "esp32s2"
        self.assertTrue(inspect(d)["ready"])

    def test_no_download_evidence(self):
        d = self.fixture()
        d["ports"][0]["boot_mode"] = "flash"
        self.assertFalse(inspect(d)["ready"])

    def test_no_authorization(self):
        d = self.fixture()
        d["ports"][0]["owner_authorized"] = False
        self.assertFalse(inspect(d)["ready"])

    def test_missing_voltage_check(self):
        d = self.fixture()
        d["ports"][0]["voltage_verified"] = False
        self.assertFalse(inspect(d)["ready"])

    def test_untrusted_path(self):
        d = self.fixture()
        d["ports"][0]["path"] = "/dev/serial/by-id/../../ttyUSB0"
        self.assertFalse(inspect(d)["ready"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", nargs="?", help="Offline JSON fixture path")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(OfflineTests)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    if not args.fixture:
        parser.error("provide a JSON fixture or --self-test")
    try:
        with open(args.fixture, encoding="utf-8") as f:
            data = json.load(f)
        result = inspect(data)
    except (OSError, ValueError, TypeError):
        result = {"ready": False, "reasons": ["INVALID_OR_UNREADABLE_FIXTURE"]}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ready"] else 2


if __name__ == "__main__":
    sys.exit(main())
