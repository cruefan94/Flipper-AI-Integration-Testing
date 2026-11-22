"""Offline Arduino Uno / ESP32 / Flipper GPIO proposal preflight; no hardware access."""
import json
import sys
import unittest

VOLTAGES = {"uno": 5.0, "esp32": 3.3, "flipper": 3.3}

def check(plan):
    errors = []
    if not isinstance(plan, dict) or not isinstance(plan.get("connections"), list):
        return ["connections must be a list"]
    if not plan["connections"]:
        return ["at least one connection required"]
    for i, wire in enumerate(plan["connections"]):
        tag = f"connection {i}"
        if not isinstance(wire, dict):
            errors.append(f"{tag}: invalid object")
            continue
        src, dst = wire.get("from"), wire.get("to")
        if not isinstance(src, str) or not isinstance(dst, str) or src not in VOLTAGES or dst not in VOLTAGES or src == dst:
            errors.append(f"{tag}: unsupported endpoint pair")
            continue
        if wire.get("signal") not in ("digital", "uart_tx"):
            errors.append(f"{tag}: unsupported signal")
            continue
        if type(wire.get("common_ground")) is not bool or not wire["common_ground"]:
            errors.append(f"{tag}: common ground not confirmed")
        if type(wire.get("voltage_verified")) is not bool or not wire["voltage_verified"]:
            errors.append(f"{tag}: voltage not independently verified")
        if src == "uno" and dst in ("esp32", "flipper"):
            if wire.get("level_shifter") != "verified_5v_to_3v3":
                errors.append(f"{tag}: 5V output requires verified 3.3V level shifting")
        if wire.get("power_link") is not False:
            errors.append(f"{tag}: power-rail linking is not supported by this preflight")
    return errors

class GateTests(unittest.TestCase):
    def setUp(self):
        self.safe = {"connections": [{"from": "uno", "to": "esp32", "signal": "uart_tx", "common_ground": True, "voltage_verified": True, "level_shifter": "verified_5v_to_3v3", "power_link": False}]}
    def test_safe(self): self.assertEqual(check(self.safe), [])
    def test_missing_shifter(self):
        self.safe["connections"][0].pop("level_shifter")
        self.assertTrue(check(self.safe))
    def test_no_ground(self):
        self.safe["connections"][0]["common_ground"] = False
        self.assertTrue(check(self.safe))
    def test_unverified_voltage(self):
        self.safe["connections"][0]["voltage_verified"] = False
        self.assertTrue(check(self.safe))
    def test_power_link(self):
        self.safe["connections"][0]["power_link"] = True
        self.assertTrue(check(self.safe))
    def test_bad_endpoints(self):
        self.safe["connections"][0]["to"] = ["esp32"]
        self.assertTrue(check(self.safe))
    def test_bad_connection(self): self.assertTrue(check({"connections": [None]}))
    def test_empty(self): self.assertTrue(check({"connections": []}))
    def test_bool_string(self):
        self.safe["connections"][0]["common_ground"] = "true"
        self.assertTrue(check(self.safe))

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 2:
        try:
            with open(sys.argv[1], encoding="utf-8") as f:
                proposal = json.load(f)
            findings = check(proposal)
            print(json.dumps({"safe_for_review": not findings, "findings": findings}, indent=2))
            sys.exit(1 if findings else 0)
        except (OSError, ValueError, TypeError):
            print(json.dumps({"safe_for_review": False, "findings": ["invalid or unreadable JSON proposal"]}))
            sys.exit(2)
    else:
        print("Usage: python3 arduino_gpio_gate.py --self-test | proposal.json")
        sys.exit(2)
