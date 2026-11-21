#!/usr/bin/env python3
"""Offline Arduino Uno / ESP32 modular sensor wiring preflight.

Accepts ONLY a local JSON plan. No serial, GPIO, network, flashing, or radio I/O.
Usage: python3 lab/arduino_sensor_manifest_preflight.py plan.json
       python3 lab/arduino_sensor_manifest_preflight.py --self-test
This is a conservative review gate, not an electrical certification.
"""
import json
import sys
import unittest
from pathlib import Path

ALLOWED_BUSES = {"digital", "analog", "uart", "i2c"}
ALLOWED_LEVELS = {3.3, 5.0}

def validate(plan):
    errors = []
    if not isinstance(plan, dict) or not isinstance(plan.get("connections"), list):
        return ["plan.connections must be a list"]
    if not plan["connections"]:
        errors.append("at least one connection required for review")
    if plan.get("common_ground_verified") is not True:
        errors.append("common ground must be independently verified")
    if plan.get("board_schematics_reviewed") is not True:
        errors.append("board schematics must be reviewed")
    seen_destinations = set()
    for i, c in enumerate(plan["connections"]):
        tag = f"connections[{i}]"
        if not isinstance(c, dict):
            errors.append(f"{tag}: connection must be object")
            continue
        required = ("source_board", "source_pin", "destination_board", "destination_pin",
                    "bus", "source_voltage", "destination_max_voltage", "direction")
        if any(not c.get(k) and c.get(k) != 0 for k in required):
            errors.append(f"{tag}: missing required field")
            continue
        if c["bus"] not in ALLOWED_BUSES or c["direction"] not in ("output-to-input", "bidirectional"):
            errors.append(f"{tag}: unsupported bus/direction")
            continue
        if (type(c["source_voltage"]) not in (int, float) or
                type(c["destination_max_voltage"]) not in (int, float) or
                c["source_voltage"] not in ALLOWED_LEVELS or
                c["destination_max_voltage"] not in ALLOWED_LEVELS):
            errors.append(f"{tag}: unsupported or unverified voltage domain")
            continue
        destination = (str(c["destination_board"]), str(c["destination_pin"]))
        if destination in seen_destinations:
            errors.append(f"{tag}: duplicate destination pin")
        seen_destinations.add(destination)
        if c["source_voltage"] > c["destination_max_voltage"] and c.get("level_shifter_verified") is not True:
            errors.append(f"{tag}: overvoltage risk without verified level shifter")
        if c["bus"] == "i2c":
            if c.get("pullup_voltage_verified") is not True:
                errors.append(f"{tag}: I2C pull-up voltage not verified")
            pullup = c.get("pullup_voltage")
            if type(pullup) not in (int, float) or pullup not in ALLOWED_LEVELS:
                errors.append(f"{tag}: I2C pull-up voltage missing or invalid")
            elif pullup > c["destination_max_voltage"]:
                errors.append(f"{tag}: I2C pull-ups exceed destination rating")
        if c["direction"] == "bidirectional" and c.get("bidirectional_voltage_verified") is not True:
            errors.append(f"{tag}: bidirectional voltage compatibility unverified")
    return errors

class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.base = {"common_ground_verified": True, "board_schematics_reviewed": True,
                     "connections": [{"source_board": "Uno", "source_pin": "D2",
                                      "destination_board": "ESP32", "destination_pin": "GPIO18",
                                      "bus": "digital", "direction": "output-to-input",
                                      "source_voltage": 5.0, "destination_max_voltage": 3.3,
                                      "level_shifter_verified": True}]}
    def test_verified_level_shift(self):
        self.assertEqual(validate(self.base), [])
    def test_reject_unshifted_5v(self):
        self.base["connections"][0]["level_shifter_verified"] = False
        self.assertTrue(any("overvoltage" in e for e in validate(self.base)))
    def test_reject_missing_ground(self):
        self.base["common_ground_verified"] = False
        self.assertTrue(validate(self.base))
    def test_reject_missing_schematic(self):
        self.base["board_schematics_reviewed"] = False
        self.assertTrue(validate(self.base))
    def test_reject_duplicate_pin(self):
        self.base["connections"].append(dict(self.base["connections"][0]))
        self.assertTrue(any("duplicate" in e for e in validate(self.base)))
    def test_reject_i2c_unverified_pullup(self):
        self.base["connections"][0]["bus"] = "i2c"
        self.assertTrue(any("pull-up" in e for e in validate(self.base)))
    def test_reject_bidirectional_unverified(self):
        self.base["connections"][0]["direction"] = "bidirectional"
        self.assertTrue(any("bidirectional" in e for e in validate(self.base)))
    def test_reject_unknown_domain(self):
        self.base["connections"][0]["source_voltage"] = 12
        self.assertTrue(validate(self.base))
    def test_reject_invalid_plan(self):
        self.assertTrue(validate([]))
    def test_empty_plan_not_approval(self):
        self.base["connections"] = []
        self.assertTrue(any("at least one" in e for e in validate(self.base)))
    def test_reject_string_voltage(self):
        self.base["connections"][0]["source_voltage"] = "5.0"
        self.assertTrue(validate(self.base))
    def test_reject_missing_i2c_pullup(self):
        c = self.base["connections"][0]
        c["bus"] = "i2c"
        c["pullup_voltage_verified"] = True
        self.assertTrue(any("pull-up voltage missing" in e for e in validate(self.base)))
    def test_reject_string_i2c_pullup(self):
        c = self.base["connections"][0]
        c["bus"] = "i2c"
        c["pullup_voltage_verified"] = True
        c["pullup_voltage"] = "3.3"
        self.assertTrue(any("invalid" in e for e in validate(self.base)))

if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 2:
        try:
            plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
            problems = validate(plan)
            for problem in problems:
                print("BLOCKED:", problem)
            if problems:
                sys.exit(1)
            print("PLAN REVIEW PASSED (not hardware approval)")
        except (OSError, ValueError, TypeError) as exc:
            print("BLOCKED: invalid local plan:", exc, file=sys.stderr)
            sys.exit(2)
    else:
        print(__doc__)
        sys.exit(2)
