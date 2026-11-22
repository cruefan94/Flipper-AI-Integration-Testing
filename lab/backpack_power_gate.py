#!/usr/bin/env python3
"""Public-safe OFFLINE Flipper/ESP32 backpack power-plan gate.

Only evaluates supplied JSON; never reads GPIO, USB, serial or hardware.
Input example: {"source_voltage_v":5,"source_continuous_ma":2000,
"source_verified":true,"owner_approved":true,"loads":[
{"name":"esp32","voltage_v":5,"peak_ma":500,"verified":true}]}
Numbers are measured/nameplate evidence, NOT recommended hardware ratings.
"""
import json
import math
import sys
import unittest

def valid_number(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0

def evaluate(plan):
    errors = []
    if not isinstance(plan, dict):
        return ["plan must be an object"]
    for key in ("source_voltage_v", "source_continuous_ma"):
        if not valid_number(plan.get(key)):
            errors.append(key + " must be a positive finite number")
    for key in ("source_verified", "owner_approved"):
        if plan.get(key) is not True:
            errors.append(key + " must be explicitly true")
    loads = plan.get("loads")
    if not isinstance(loads, list) or not loads:
        errors.append("loads must be a nonempty list")
        return errors
    seen = set()
    total = 0
    for index, load in enumerate(loads):
        prefix = "loads[%d]" % index
        if not isinstance(load, dict):
            errors.append(prefix + " must be an object")
            continue
        name = load.get("name")
        if not isinstance(name, str) or not name.strip() or " ".join(name.split()).casefold() in seen:
            errors.append(prefix + " name must be unique and nonempty")
        else:
            seen.add(" ".join(name.split()).casefold())
        for key in ("voltage_v", "peak_ma"):
            if not valid_number(load.get(key)):
                errors.append(prefix + " " + key + " invalid")
        if load.get("verified") is not True:
            errors.append(prefix + " requires verified ratings")
        if valid_number(load.get("voltage_v")) and valid_number(plan.get("source_voltage_v")):
            if load["voltage_v"] != plan["source_voltage_v"]:
                errors.append(prefix + " voltage differs; converter/rail evidence required")
        if valid_number(load.get("peak_ma")):
            total += load["peak_ma"]
    if valid_number(plan.get("source_continuous_ma")) and total > plan["source_continuous_ma"] * 0.8:
        errors.append("peak load sum exceeds 80% conservative source budget")
    return errors

class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.good = dict(source_voltage_v=5, source_continuous_ma=2000,
                         source_verified=True, owner_approved=True,
                         loads=[dict(name="board", voltage_v=5, peak_ma=500, verified=True)])
    def test_valid(self): self.assertEqual(evaluate(self.good), [])
    def test_boolean_as_current(self):
        self.good["loads"][0]["peak_ma"] = True
        self.assertTrue(evaluate(self.good))
    def test_nan(self):
        self.good["source_continuous_ma"] = float("nan")
        self.assertTrue(evaluate(self.good))
    def test_oversubscription(self):
        self.good["loads"][0]["peak_ma"] = 1700
        self.assertTrue(evaluate(self.good))
    def test_wrong_rail(self):
        self.good["loads"][0]["voltage_v"] = 3.3
        self.assertTrue(evaluate(self.good))
    def test_missing_consent(self):
        self.good["owner_approved"] = False
        self.assertTrue(evaluate(self.good))
    def test_duplicate_load(self):
        self.good["loads"].append(self.good["loads"][0].copy())
        self.assertTrue(evaluate(self.good))
    def test_duplicate_case_alias(self):
        self.good["loads"].append(dict(name="BOARD", voltage_v=5, peak_ma=500, verified=True))
        self.assertTrue(evaluate(self.good))
    def test_duplicate_whitespace_alias(self):
        self.good["loads"][0]["name"] = "esp32  wroom"
        self.good["loads"].append(dict(name=" esp32 wroom ", voltage_v=5, peak_ma=500, verified=True))
        self.assertTrue(evaluate(self.good))
    def test_distinct_load_names(self):
        self.good["loads"].append(dict(name="other", voltage_v=5, peak_ma=500, verified=True))
        self.assertEqual(evaluate(self.good), [])
    def test_malformed_load(self):
        self.good["loads"] = [None]
        self.assertTrue(evaluate(self.good))

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 2:
        try:
            with open(sys.argv[1], encoding="utf-8") as handle:
                errors = evaluate(json.load(handle))
        except (OSError, ValueError) as exc:
            print("REJECT: invalid evidence file:", type(exc).__name__)
            sys.exit(2)
        print("REJECT: " + "; ".join(errors) if errors else "PASS: offline plan only; physical safety NOT verified")
        sys.exit(1 if errors else 0)
    else:
        print("Usage: python3 backpack_power_gate.py --self-test | plan.json")
        sys.exit(2)
