#!/usr/bin/env python3
"""Offline ESP32 boot-observation triage. Never accesses ports or hardware."""
import json
import sys
import unittest

ALLOWED_CHIPS = {"esp32-wroom", "esp32-s2"}
ALLOWED_STATES = {"held-low", "released-high", "unknown"}
ALLOWED_USB = {"enumerated", "absent", "unknown"}
FIELDS = {"chip", "boot", "en", "usb", "power_verified", "owner_observed"}

def triage(record):
    if not isinstance(record, dict) or set(record) != FIELDS:
        return {"status": "BLOCKED", "reason": "schema"}
    if record["chip"] not in ALLOWED_CHIPS or record["boot"] not in ALLOWED_STATES or record["en"] not in ALLOWED_STATES or record["usb"] not in ALLOWED_USB:
        return {"status": "BLOCKED", "reason": "invalid observation"}
    if type(record["power_verified"]) is not bool or type(record["owner_observed"]) is not bool:
        return {"status": "BLOCKED", "reason": "invalid confirmation"}
    if not record["owner_observed"] or not record["power_verified"]:
        return {"status": "BLOCKED", "reason": "owner/power confirmation missing"}
    if "unknown" in (record["boot"], record["en"], record["usb"]):
        return {"status": "REVIEW", "reason": "incomplete observations"}
    if record["en"] == "held-low":
        return {"status": "REVIEW", "reason": "reset held; no boot inference"}
    if record["boot"] == "held-low":
        return {"status": "REVIEW", "reason": "boot strap observed low; ROM state unverified"}
    return {"status": "REVIEW", "reason": "normal strap observed; firmware state unverified"}

class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.good = dict(chip="esp32-wroom", boot="released-high", en="released-high",
                         usb="enumerated", power_verified=True, owner_observed=True)
    def test_normal_never_approves_flash(self):
        self.assertEqual(triage(self.good)["status"], "REVIEW")
    def test_boot_low_not_flash_permission(self):
        self.assertEqual(triage(dict(self.good, boot="held-low"))["status"], "REVIEW")
    def test_en_low_reset(self):
        self.assertIn("reset", triage(dict(self.good, en="held-low"))["reason"])
    def test_unknown(self):
        self.assertEqual(triage(dict(self.good, usb="unknown"))["status"], "REVIEW")
    def test_missing_power(self):
        self.assertEqual(triage(dict(self.good, power_verified=False))["status"], "BLOCKED")
    def test_no_owner_observation(self):
        self.assertEqual(triage(dict(self.good, owner_observed=False))["status"], "BLOCKED")
    def test_s2_separate(self):
        self.assertEqual(triage(dict(self.good, chip="esp32-s2"))["status"], "REVIEW")
    def test_reject_extra_private_data(self):
        self.assertEqual(triage(dict(self.good, serial="secret"))["status"], "BLOCKED")
    def test_reject_nonboolean(self):
        self.assertEqual(triage(dict(self.good, power_verified=1))["status"], "BLOCKED")
    def test_reject_unknown_chip(self):
        self.assertEqual(triage(dict(self.good, chip="other"))["status"], "BLOCKED")

if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 1:
        try:
            payload = json.load(sys.stdin)
            print(json.dumps(triage(payload), sort_keys=True))
        except (ValueError, TypeError):
            print(json.dumps({"status": "BLOCKED", "reason": "invalid JSON"}))
            sys.exit(2)
    else:
        print("Usage: script.py [--self-test] < anonymous-observation.json", file=sys.stderr)
        sys.exit(2)
