#!/usr/bin/env python3
"""Offline ESP32 ROM boot-message classifier. No serial ports, GPIO or flashing."""
import argparse
import json
import re
import sys
import unittest

MAX_BYTES = 8192
BOOT_RE = re.compile(r"boot:0x([0-9a-fA-F]{1,2})\b")
RESET_RE = re.compile(r"rst:0x([0-9a-fA-F]{1,2})\b")
SENSITIVE = re.compile(r"(?i)(/dev/|COM[0-9]+|serial\s*(?:number|no)|mac\s*[:=]|ssid|password|token|key\s*[:=])")

def classify(text):
    if not isinstance(text, str) or not text or len(text.encode("utf-8")) > MAX_BYTES:
        return {"status": "REJECTED", "reason": "empty or oversized input"}
    if SENSITIVE.search(text):
        return {"status": "REJECTED", "reason": "possible device identifier or secret"}
    boots = BOOT_RE.findall(text)
    resets = RESET_RE.findall(text)
    if len(boots) != 1 or len(resets) != 1:
        return {"status": "INCOMPLETE", "reason": "require exactly one rst and boot code"}
    boot = int(boots[0], 16)
    # ESP32 classic GPIO0 strap is bit 4; ESP32-S2 uses different ROM/straps.
    # This is intentionally NOT a flashing permission or chip identification.
    return {"status": "OBSERVED", "reset_code": "0x" + resets[0].lower(),
            "boot_code": "0x" + boots[0].lower(),
            "gpio0_strap_low_classic_esp32": (boot & 0x10) == 0,
            "caution": "Only classic ESP32 strap hint; verify exact chip/board. No flash approval."}

class Tests(unittest.TestCase):
    def test_typical_download_hint(self):
        self.assertTrue(classify("rst:0x1 (POWERON_RESET),boot:0x3 (DOWNLOAD_BOOT)")["gpio0_strap_low_classic_esp32"])
    def test_typical_normal_hint(self):
        self.assertFalse(classify("rst:0x1,boot:0x13")["gpio0_strap_low_classic_esp32"])
    def test_missing(self):
        self.assertEqual(classify("waiting for download")["status"], "INCOMPLETE")
    def test_ambiguous(self):
        self.assertEqual(classify("rst:0x1 boot:0x3 boot:0x13")["status"], "INCOMPLETE")
    def test_identifier(self):
        self.assertEqual(classify("rst:0x1 boot:0x3 MAC: aa:bb")["status"], "REJECTED")
    def test_oversize(self):
        self.assertEqual(classify("x" * 9000)["status"], "REJECTED")
    def test_no_execution(self):
        self.assertEqual(classify("rst:0x1 boot:0x3")["status"], "OBSERVED")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify pasted sanitized ESP32 ROM text, offline; never accesses devices")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--text", help="Short sanitized ROM boot text (no identifiers)")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=[sys.argv[0]], exit=False)
    elif args.text is not None:
        print(json.dumps(classify(args.text), sort_keys=True))
    else:
        parser.error("provide --text or --self-test")
