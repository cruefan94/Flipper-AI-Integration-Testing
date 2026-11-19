"""Offline ESP32 ROM-handshake evidence classifier. Never opens ports or flashes devices.

Input must be sanitized, public-safe synthetic diagnostic text only.
No raw private device logs, serial numbers, addresses, or credentials in CI.
"""
import re
import unittest

MAX_LOG_CHARS = 8192
CHIPS = {"esp32", "esp32s2"}


def classify(chip: str, diagnostic: str) -> dict:
    """Classify a sanitized esptool diagnostic; never treat text as proof of hardware."""
    if chip not in CHIPS:
        return {"status": "INVALID_INPUT", "reason": "unsupported_chip"}
    if not isinstance(diagnostic, str) or len(diagnostic) > MAX_LOG_CHARS:
        return {"status": "INVALID_INPUT", "reason": "invalid_length"}
    # Fail closed: no raw diagnostic text is ever returned.
    lower = diagnostic.lower()
    if any(s in lower for s in ("password=", "token=", "authorization:", "-----begin private key")):
        return {"status": "INVALID_INPUT", "reason": "sensitive_content"}
    if re.search(r"failed to connect|no serial data received|wrong boot mode|timed out waiting for packet", lower):
        return {"status": "NOT_CONFIRMED", "reason": "rom_handshake_failed"}
    # Only accept a positive ROM identification plus a matching chip family.
    match = re.search(r"detecting chip type\.\.\.\s*(esp32-s2|esp32)", lower)
    if match:
        observed = match.group(1).replace("-", "")
        if observed != chip:
            return {"status": "NOT_CONFIRMED", "reason": "chip_mismatch"}
        return {"status": "DIAGNOSTIC_ONLY", "reason": "rom_identification_reported"}
    return {"status": "NOT_CONFIRMED", "reason": "no_rom_identification"}


class ClassifierTests(unittest.TestCase):
    def test_esp32(self):
        self.assertEqual(classify("esp32", "Detecting chip type... ESP32")["status"], "DIAGNOSTIC_ONLY")

    def test_s2(self):
        self.assertEqual(classify("esp32s2", "Detecting chip type... ESP32-S2")["status"], "DIAGNOSTIC_ONLY")

    def test_mismatch(self):
        self.assertEqual(classify("esp32", "Detecting chip type... ESP32-S2")["reason"], "chip_mismatch")

    def test_timeout(self):
        self.assertEqual(classify("esp32", "Timed out waiting for packet")["status"], "NOT_CONFIRMED")

    def test_failure_precedence(self):
        self.assertEqual(classify("esp32", "Detecting chip type... ESP32\nFailed to connect")["status"], "NOT_CONFIRMED")

    def test_empty(self):
        self.assertEqual(classify("esp32", "")["reason"], "no_rom_identification")

    def test_unsupported(self):
        self.assertEqual(classify("esp8266", "Detecting chip type... ESP32")["status"], "INVALID_INPUT")

    def test_secrets(self):
        self.assertEqual(classify("esp32", "token=SECRET")["reason"], "sensitive_content")

    def test_oversize(self):
        self.assertEqual(classify("esp32", "x" * 8193)["status"], "INVALID_INPUT")

    def test_no_raw_output(self):
        self.assertNotIn("diagnostic", classify("esp32", "unrecognized synthetic content"))


if __name__ == "__main__":
    unittest.main()
