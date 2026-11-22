#!/usr/bin/env python3
"""Offline ESP32-WROOM/Pi serial wiring preflight. No serial access or flashing."""
import argparse
import json
import re
import sys
import unittest

PORT_RE = re.compile(r"^/dev/tty(?:USB|ACM)[0-9]{1,3}$")
EXPECTED_SEQUENCE = ["hold_boot_low", "pulse_en_low", "release_en", "release_boot"]

def validate(plan):
    if not isinstance(plan, dict):
        return ["plan must be a JSON object"]
    errors = []
    if plan.get("chip") != "ESP32-WROOM-32":
        errors.append("chip must be ESP32-WROOM-32; S2/S3 require separate procedures")
    port = plan.get("port")
    if not isinstance(port, str) or not PORT_RE.fullmatch(port):
        errors.append("port must be /dev/ttyUSB<N> or /dev/ttyACM<N>")
    voltage = plan.get("uart_logic_volts")
    if type(voltage) not in (int, float) or voltage != 3.3:
        errors.append("USB-UART TX/RX logic must be explicitly 3.3 V")
    if plan.get("common_ground") is not True:
        errors.append("common ground must be confirmed")
    if plan.get("tx_to_rx") is not True or plan.get("rx_to_tx") is not True:
        errors.append("crossed TX/RX must be confirmed")
    if plan.get("boot_sequence") != EXPECTED_SEQUENCE:
        errors.append("BOOT(GPIO0)/EN sequence does not match manual ROM download entry")
    if plan.get("external_power_verified") is not True:
        errors.append("power source and 3.3 V regulator must be verified separately")
    return errors

class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.good = dict(chip="ESP32-WROOM-32", port="/dev/ttyUSB0",
                         uart_logic_volts=3.3, common_ground=True,
                         tx_to_rx=True, rx_to_tx=True,
                         boot_sequence=EXPECTED_SEQUENCE.copy(),
                         external_power_verified=True)
    def test_valid(self):
        self.assertEqual(validate(self.good), [])
    def test_5v(self):
        self.good["uart_logic_volts"] = 5
        self.assertTrue(validate(self.good))
    def test_bool_voltage(self):
        self.good["uart_logic_volts"] = True
        self.assertTrue(validate(self.good))
    def test_injection_port(self):
        self.good["port"] = "/dev/ttyUSB0;rm -rf /"
        self.assertTrue(validate(self.good))
    def test_s2_is_separate(self):
        self.good["chip"] = "ESP32-S2"
        self.assertTrue(validate(self.good))
    def test_missing_ground(self):
        self.good["common_ground"] = False
        self.assertTrue(validate(self.good))
    def test_wrong_sequence(self):
        self.good["boot_sequence"] = list(reversed(EXPECTED_SEQUENCE))
        self.assertTrue(validate(self.good))
    def test_missing_power(self):
        self.good["external_power_verified"] = False
        self.assertTrue(validate(self.good))
    def test_empty(self):
        self.assertTrue(validate({}))

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--plan", help="Path to offline JSON wiring plan")
    args = parser.parse_args(argv)
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(OfflineTests)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    if not args.plan:
        parser.error("specify --plan or --self-test")
    try:
        with open(args.plan, encoding="utf-8") as f:
            plan = json.load(f)
    except (OSError, ValueError) as exc:
        print("INVALID: unable to read JSON plan: " + str(exc), file=sys.stderr)
        return 2
    errors = validate(plan)
    for error in errors:
        print("BLOCKED: " + error)
    if errors:
        return 2
    print("STATIC PLAN PASS ONLY. No hardware inspected; do not flash.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
