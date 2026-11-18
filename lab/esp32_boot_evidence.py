#!/usr/bin/env python3
"""Offline ESP32 boot-mode evidence validator. Never opens ports or flashes hardware."""
import json
import sys
import unittest

VALID_CHIPS = {"esp32-wroom", "esp32-s2"}
def inspect(record):
    if not isinstance(record, dict):
        return ["record must be an object"]
    issues = []
    if record.get("chip") not in VALID_CHIPS:
        issues.append("unknown chip family")
    if record.get("transport") != "usb-serial":
        issues.append("transport must be usb-serial")
    if record.get("authorization") is not True:
        issues.append("owner authorization missing")
    steps = record.get("steps")
    if not isinstance(steps, list):
        return issues + ["steps must be a list"]
    expected = [
        ("hold_boot", 0, 1),
        ("assert_en", 0, 0),
        ("release_en", 1, 0),
        ("release_boot", 1, 1),
    ]
    if len(steps) != len(expected):
        issues.append("expected four ordered steps")
        return issues
    for i, (action, en, boot) in enumerate(expected):
        step = steps[i]
        if not isinstance(step, dict) or (step.get("action"), step.get("en"), step.get("boot")) != (action, en, boot):
            issues.append("step %d does not match expected EN/BOOT state" % (i + 1))
    if record.get("rom_download_mode_observed") is not True:
        issues.append("ROM download-mode observation absent")
    return issues

class Tests(unittest.TestCase):
    def setUp(self):
        self.good = {"chip":"esp32-wroom","transport":"usb-serial","authorization":True,
                     "steps":[{"action":a,"en":e,"boot":b} for a,e,b in [
                         ("hold_boot",0,1),("assert_en",0,0),
                         ("release_en",1,0),("release_boot",1,1)]],
                     "rom_download_mode_observed":True}
    def test_valid(self): self.assertEqual(inspect(self.good), [])
    def test_s2(self):
        self.good["chip"]="esp32-s2"
        self.assertEqual(inspect(self.good), [])
    def test_unknown_chip(self):
        self.good["chip"]="esp32-c3"
        self.assertIn("unknown chip family",inspect(self.good))
    def test_no_authorization(self):
        self.good["authorization"]=False
        self.assertIn("owner authorization missing",inspect(self.good))
    def test_wrong_transport(self):
        self.good["transport"]="wifi"
        self.assertTrue(inspect(self.good))
    def test_no_rom_evidence(self):
        self.good["rom_download_mode_observed"]=False
        self.assertTrue(inspect(self.good))
    def test_bad_order(self):
        self.good["steps"][1],self.good["steps"][2]=self.good["steps"][2],self.good["steps"][1]
        self.assertTrue(inspect(self.good))
    def test_bad_boot_level(self):
        self.good["steps"][2]["boot"]=1
        self.assertTrue(inspect(self.good))
    def test_malformed_steps(self):
        self.good["steps"]="bad"
        self.assertTrue(inspect(self.good))
    def test_non_object(self): self.assertTrue(inspect(None))

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv)==2:
        try:
            with open(sys.argv[1],encoding="utf-8") as f: data=json.load(f)
            issues=inspect(data)
            print(json.dumps({"status":"REJECT" if issues else "EVIDENCE_COMPLETE_NOT_FLASH_APPROVAL","issues":issues}))
            sys.exit(1 if issues else 0)
        except (OSError,ValueError) as exc:
            print(json.dumps({"status":"REJECT","issues":[type(exc).__name__]}))
            sys.exit(2)
    else:
        print("Usage: python esp32_boot_evidence.py observation.json | --self-test")
        sys.exit(2)
