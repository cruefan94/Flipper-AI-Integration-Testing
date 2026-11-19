"""Offline public-safe ROM banner evidence classifier; never opens hardware."""
import re
import unittest

CHIPS = {
    "ESP32": re.compile(r"^Chip is ESP32(?=\s|\(|$)", re.I | re.M),
    "ESP32-S2": re.compile(r"^Chip is ESP32-S2\b", re.I | re.M),
}

def classify(log, expected):
    if expected not in CHIPS or not isinstance(log, str) or len(log) > 4096:
        return "INVALID_INPUT"
    if re.search(r"(?i)(token|password|api[_-]?key|authorization)\s*[:=]", log):
        return "REDACT_REQUIRED"
    if re.search(r"(?i)A fatal error occurred:|timed out|failed to connect|no serial data received", log):
        return "CONNECT_FAILED"
    seen = [name for name, pattern in CHIPS.items() if pattern.search(log)]
    if len(seen) != 1:
        return "AMBIGUOUS_OR_MISSING_CHIP"
    if seen[0] != expected:
        return "CHIP_MISMATCH"
    if not re.search(r"(?im)^Connecting\.{1,}$", log):
        return "INCOMPLETE_EVIDENCE"
    return "ROM_HANDSHAKE_REPORTED_NOT_VERIFIED"

class Tests(unittest.TestCase):
    def test_wroom(self):
        self.assertEqual(classify("Connecting...\nChip is ESP32 (revision v1)", "ESP32"), "ROM_HANDSHAKE_REPORTED_NOT_VERIFIED")
    def test_s2(self):
        self.assertEqual(classify("Connecting...\nChip is ESP32-S2 (revision v0)", "ESP32-S2"), "ROM_HANDSHAKE_REPORTED_NOT_VERIFIED")
    def test_mismatch(self):
        self.assertEqual(classify("Connecting...\nChip is ESP32-S2", "ESP32"), "CHIP_MISMATCH")
    def test_no_connect(self):
        self.assertEqual(classify("Chip is ESP32", "ESP32"), "INCOMPLETE_EVIDENCE")
    def test_failed(self):
        self.assertEqual(classify("Connecting...\nChip is ESP32\nA fatal error occurred: failed to connect", "ESP32"), "CONNECT_FAILED")
    def test_ambiguous(self):
        self.assertEqual(classify("Connecting...\nChip is ESP32\nChip is ESP32-S2", "ESP32"), "AMBIGUOUS_OR_MISSING_CHIP")
    def test_oversized(self):
        self.assertEqual(classify("x" * 4097, "ESP32"), "INVALID_INPUT")
    def test_secret(self):
        self.assertEqual(classify("Connecting...\nChip is ESP32\ntoken: abc", "ESP32"), "REDACT_REQUIRED")
    def test_unknown(self):
        self.assertEqual(classify("Connecting...", "ESP32-C3"), "INVALID_INPUT")

if __name__ == "__main__":
    unittest.main()
