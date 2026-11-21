"""Offline, non-authorizing ESP32 ROM boot log classifier.

No serial access, GPIO toggling, flashing, network, or board discovery.
A classic ESP32 boot line must not be interpreted as ESP32-S2 evidence.
"""
import re
import unittest

CLASSIC_BOOT = re.compile(r"^rst:0x([0-9a-fA-F]+) \([^\r\n]{1,64}\),boot:0x([0-9a-fA-F]+) \([^\r\n]{1,64}\)$")
MAX_LENGTH = 4096

def classify_rom_log(chip, log):
    if chip not in ("ESP32", "ESP32-S2"):
        return {"status": "REVIEW", "reason": "unknown_chip", "flash_allowed": False}
    if not isinstance(log, str) or len(log) > MAX_LENGTH or "\x00" in log:
        return {"status": "REVIEW", "reason": "invalid_input", "flash_allowed": False}
    lines = [line.strip() for line in log.splitlines() if line.strip()]
    matches = [CLASSIC_BOOT.fullmatch(line) for line in lines]
    matches = [match for match in matches if match]
    if chip == "ESP32-S2":
        return {"status": "REVIEW", "reason": "s2_requires_chip_specific_rom_validation", "flash_allowed": False}
    if len(matches) != 1:
        return {"status": "REVIEW", "reason": "missing_or_ambiguous_classic_rom_line", "flash_allowed": False}
    return {
        "status": "OBSERVED",
        "reason": "classic_esp32_rom_line_only",
        "reset_code": matches[0].group(1).lower(),
        "boot_code": matches[0].group(2).lower(),
        "flash_allowed": False,
    }

class RomFamilySafetyTests(unittest.TestCase):
    SAMPLE = "rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)"
    def test_classic_observation(self):
        self.assertEqual(classify_rom_log("ESP32", self.SAMPLE)["boot_code"], "13")
    def test_s2_not_inferred_from_classic(self):
        self.assertEqual(classify_rom_log("ESP32-S2", self.SAMPLE)["status"], "REVIEW")
    def test_unknown_family(self):
        self.assertEqual(classify_rom_log("ESP32-C3", self.SAMPLE)["reason"], "unknown_chip")
    def test_no_line(self):
        self.assertEqual(classify_rom_log("ESP32", "waiting for download")["status"], "REVIEW")
    def test_duplicate_lines(self):
        self.assertEqual(classify_rom_log("ESP32", self.SAMPLE + "\n" + self.SAMPLE)["status"], "REVIEW")
    def test_nul(self):
        self.assertEqual(classify_rom_log("ESP32", self.SAMPLE + "\x00")["status"], "REVIEW")
    def test_long_input(self):
        self.assertEqual(classify_rom_log("ESP32", "x" * 4097)["status"], "REVIEW")
    def test_no_flash_authorization(self):
        for chip in ("ESP32", "ESP32-S2", "other"):
            self.assertFalse(classify_rom_log(chip, self.SAMPLE)["flash_allowed"])

if __name__ == "__main__":
    unittest.main()
