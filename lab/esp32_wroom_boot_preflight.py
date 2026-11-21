#!/usr/bin/env python3
"""Offline ESP32-WROOM boot-mode preflight. Never opens ports, drives GPIO, or flashes."""
import argparse
import json
import unittest

VALID_LEVELS = {"low", "high", "unknown"}
def assess(record):
    """Review owner-recorded levels; fail closed on missing/uncertain evidence."""
    reasons = []
    if record.get("chip") != "esp32-wroom":
        reasons.append("board identity not confirmed as classic ESP32-WROOM")
    for key in ("en", "gpio0", "gpio2", "gpio12"):
        if record.get(key) not in VALID_LEVELS:
            reasons.append(f"{key}: missing or invalid observation")
        elif record[key] == "unknown":
            reasons.append(f"{key}: level not measured")
    if record.get("supply_verified_3v3") is not True:
        reasons.append("3.3V supply not verified")
    if record.get("ground_shared") is not True:
        reasons.append("common ground not verified")
    if record.get("external_5v_gpio") is not False:
        reasons.append("possible 5V GPIO exposure")
    if record.get("en") == "low":
        reasons.append("EN held low: chip remains reset")
    if record.get("gpio0") == "high":
        reasons.append("GPIO0 high: normal boot, not UART download mode")
    if record.get("gpio2") == "high":
        reasons.append("GPIO2 high: review boot strapping before download")
    if record.get("gpio12") == "high":
        reasons.append("GPIO12 high: may select incompatible flash voltage")
    return {"ready_for_owner_review": not reasons, "reasons": reasons,
            "warning": "Static planning only; no flash authorization or physical verification"}

class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.safe = dict(chip="esp32-wroom", en="high", gpio0="low",
                         gpio2="low", gpio12="low", supply_verified_3v3=True,
                         ground_shared=True, external_5v_gpio=False)
    def test_nominal(self):
        self.assertTrue(assess(self.safe)["ready_for_owner_review"])
    def test_wrong_chip(self):
        self.assertFalse(assess({**self.safe, "chip": "esp32-s2"})["ready_for_owner_review"])
    def test_en_reset(self):
        self.assertIn("EN held low", " ".join(assess({**self.safe, "en": "low"})["reasons"]))
    def test_gpio0_normal_boot(self):
        self.assertFalse(assess({**self.safe, "gpio0": "high"})["ready_for_owner_review"])
    def test_gpio12_flash_voltage(self):
        self.assertFalse(assess({**self.safe, "gpio12": "high"})["ready_for_owner_review"])
    def test_gpio2_strap(self):
        self.assertFalse(assess({**self.safe, "gpio2": "high"})["ready_for_owner_review"])
    def test_unknown_and_missing(self):
        self.assertFalse(assess({**self.safe, "en": "unknown", "gpio0": None})["ready_for_owner_review"])
    def test_5v_exposure(self):
        self.assertFalse(assess({**self.safe, "external_5v_gpio": True})["ready_for_owner_review"])
    def test_power_ground(self):
        self.assertFalse(assess({**self.safe, "ground_shared": False, "supply_verified_3v3": False})["ready_for_owner_review"])

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fixture", help="Local JSON observation record; no hardware access")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        unittest.main(argv=["offline-preflight"], exit=False)
    elif a.fixture:
        with open(a.fixture, encoding="utf-8") as f:
            print(json.dumps(assess(json.load(f)), indent=2))
    else:
        p.error("provide --self-test or --fixture")

if __name__ == "__main__":
    main()
