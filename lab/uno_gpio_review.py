#!/usr/bin/env python3
"""Offline, fail-closed review of proposed Arduino/ESP32/Flipper signal wiring.

This is NOT an electrical certification, board pinout database, or hardware controller.
Only public-safe synthetic fixtures; no ports, GPIO, USB or network are accessed.
"""
import json
import sys
import unittest

ALLOWED = {"arduino_uno", "esp32_wroom", "esp32_s2", "flipper_zero"}
THREE_V = {"esp32_wroom", "esp32_s2", "flipper_zero"}

def review(document):
    if not isinstance(document, dict) or not isinstance(document.get("links"), list):
        return ["BLOCK: expected an object containing links array"]
    if not document["links"]:
        return ["BLOCK: no links supplied"]
    findings = []
    for index, link in enumerate(document["links"], 1):
        label = f"link {index}"
        if not isinstance(link, dict):
            findings.append(f"BLOCK {label}: invalid link")
            continue
        src, dst = link.get("source"), link.get("target")
        if src not in ALLOWED or dst not in ALLOWED or src == dst:
            findings.append(f"BLOCK {label}: unknown or identical endpoints")
            continue
        if link.get("kind") not in {"gpio", "i2c", "uart", "power"}:
            findings.append(f"BLOCK {label}: unknown link kind")
            continue
        if link["kind"] == "power":
            findings.append(f"BLOCK {label}: power/backfeed requires schematic and measured rails")
            continue
        volts = link.get("source_high_volts")
        if isinstance(volts, bool) or not isinstance(volts, (int, float)) or not (0 <= volts <= 5.5):
            findings.append(f"BLOCK {label}: missing/invalid measured source high voltage")
            continue
        if dst in THREE_V and volts > 3.3:
            if link.get("level_shift_verified") is not True:
                findings.append(f"BLOCK {label}: over-3.3V signal into 3.3V endpoint")
                continue
        if link["kind"] == "i2c" and link.get("pullup_rail_verified") is not True:
            findings.append(f"BLOCK {label}: I2C pull-up rail unverified")
            continue
        if link.get("common_ground_verified") is not True:
            findings.append(f"BLOCK {label}: common ground unverified")
            continue
        findings.append(f"REVIEW {label}: preliminary checks only; confirm exact pins, direction and datasheets")
    return findings

class SafetyTests(unittest.TestCase):
    def link(self, **kw):
        return {"links": [dict(source="arduino_uno", target="esp32_wroom",
                               kind="uart", source_high_volts=5.0,
                               common_ground_verified=True, **kw)]}

    def test_five_volt_blocks(self):
        self.assertIn("BLOCK", review(self.link())[0])
    def test_verified_shifter_still_review(self):
        self.assertIn("REVIEW", review(self.link(level_shift_verified=True))[0])
    def test_missing_ground_blocks(self):
        x = self.link(level_shift_verified=True)
        x["links"][0]["common_ground_verified"] = False
        self.assertIn("BLOCK", review(x)[0])
    def test_i2c_pullups_block(self):
        x = self.link(level_shift_verified=True)
        x["links"][0]["kind"] = "i2c"
        self.assertIn("BLOCK", review(x)[0])
    def test_power_always_blocks(self):
        x = self.link()
        x["links"][0]["kind"] = "power"
        self.assertIn("BLOCK", review(x)[0])
    def test_unknown_board_blocks(self):
        x = self.link()
        x["links"][0]["target"] = "mystery"
        self.assertIn("BLOCK", review(x)[0])
    def test_boolean_voltage_blocks(self):
        x = self.link()
        x["links"][0]["source_high_volts"] = True
        self.assertIn("BLOCK", review(x)[0])
    def test_empty_blocks(self):
        self.assertIn("BLOCK", review({"links": []})[0])
    def test_3v3_still_review(self):
        x = self.link()
        x["links"][0]["source_high_volts"] = 3.3
        self.assertIn("REVIEW", review(x)[0])

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 2:
        try:
            with open(sys.argv[1], encoding="utf-8") as stream:
                findings = review(json.load(stream))
            print("\n".join(findings))
            sys.exit(1 if any(x.startswith("BLOCK") for x in findings) else 0)
        except (OSError, ValueError) as error:
            print("BLOCK: unreadable or invalid JSON input", file=sys.stderr)
            sys.exit(2)
    else:
        print("Usage: python3 uno_gpio_review.py <wiring.json> | --self-test", file=sys.stderr)
        sys.exit(2)
