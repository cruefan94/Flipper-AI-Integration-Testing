#!/usr/bin/env python3
"""Offline, public-safe USB inventory comparison. No USB/serial/device access.

Accepts *sanitized* lsusb-like lines on stdin or files via caller; never collects
USB data itself. Prints only VID:PID counts, not bus, device, manufacturer or serial.
"""
import collections
import re
import unittest

LINE = re.compile(r"^Bus [0-9]{3} Device [0-9]{3}: ID ([0-9a-fA-F]{4}):([0-9a-fA-F]{4})(?:\s+.*)?$")
MAX_LINES = 256
MAX_LENGTH = 256

def inventory(text):
    if not isinstance(text, str) or len(text) > MAX_LINES * MAX_LENGTH:
        raise ValueError("invalid or oversized inventory")
    lines = text.splitlines()
    if len(lines) > MAX_LINES:
        raise ValueError("too many devices")
    counts = collections.Counter()
    for line in lines:
        if len(line) > MAX_LENGTH or not line.isascii() or any(ord(c) < 32 for c in line):
            raise ValueError("unsafe inventory line")
        if not line.strip():
            continue
        match = LINE.fullmatch(line)
        if not match:
            raise ValueError("invalid USB inventory; do not include serial/path details")
        counts[f"{match[1].lower()}:{match[2].lower()}"] += 1
    return counts

def compare(before, after):
    old, new = inventory(before), inventory(after)
    added, removed = new - old, old - new
    if sum(added.values()) != 1 or removed:
        return {"status": "MANUAL_REVIEW", "added": dict(added), "removed": dict(removed)}
    return {"status": "UNVERIFIED_SINGLE_ADDITION", "added": dict(added), "removed": {}}

class OfflineTests(unittest.TestCase):
    def test_single_addition(self):
        a = "Bus 001 Device 002: ID 2109:3431 VIA Hub"
        b = a + "\nBus 001 Device 003: ID 10C4:EA60 USB UART"
        result = compare(a, b)
        self.assertEqual(result["status"], "UNVERIFIED_SINGLE_ADDITION")
        self.assertEqual(result["added"], {"10c4:ea60": 1})
    def test_no_change(self):
        a = "Bus 001 Device 002: ID 2109:3431"
        self.assertEqual(compare(a, a)["status"], "MANUAL_REVIEW")
    def test_multiple_additions(self):
        b = "Bus 001 Device 002: ID 2109:3431\nBus 001 Device 003: ID 10c4:ea60"
        self.assertEqual(compare("", b)["status"], "MANUAL_REVIEW")
    def test_removal(self):
        a = "Bus 001 Device 002: ID 2109:3431"
        self.assertEqual(compare(a, "")["status"], "MANUAL_REVIEW")
    def test_bad_path(self):
        with self.assertRaises(ValueError):
            inventory("/dev/ttyUSB0")
    def test_reject_unicode(self):
        with self.assertRaises(ValueError):
            inventory("Bus 001 Device 002: ID 2109:3431 ☃")
    def test_reject_control(self):
        with self.assertRaises(ValueError):
            inventory("Bus 001 Device 002: ID 2109:3431\tserial")
    def test_reject_overlong(self):
        with self.assertRaises(ValueError):
            inventory("Bus 001 Device 002: ID 2109:3431 " + "A" * 300)
    def test_duplicate_vid_pid(self):
        a = "Bus 001 Device 002: ID 2109:3431"
        self.assertEqual(compare(a, a + "\nBus 001 Device 003: ID 2109:3431")["added"], {"2109:3431": 1})
    def test_invalid_id(self):
        with self.assertRaises(ValueError):
            inventory("Bus 001 Device 002: ID xxxx:yyyy")

if __name__ == "__main__":
    unittest.main()
