"""Offline ESP32 boot-log classifier. No hardware, serial or network access."""
import argparse
import json
import re
import unittest

CHIPS = {"esp32-wroom-32", "esp32-s2"}
BOOT = re.compile(r"boot:0x([0-9a-fA-F]{1,2})\b")
DOWNLOAD = re.compile(r"(?<![A-Za-z0-9_])(?:DOWNLOAD_BOOT\b|DOWNLOAD\(USB/UART0\)(?![A-Za-z0-9_])|waiting for download\b)", re.I)

def classify(record):
    """Classify operator-supplied text; never issue flash/reset commands."""
    if not isinstance(record, dict) or set(record) != {"chip", "observation"}:
        return {"status": "INVALID", "action": "NONE", "reason": "Expected chip and observation only"}
    chip, obs = record["chip"], record["observation"]
    if chip not in CHIPS or not isinstance(obs, str) or not obs or len(obs) > 4096:
        return {"status": "INVALID", "action": "NONE", "reason": "Unknown chip or invalid observation"}
    if DOWNLOAD.search(obs):
        return {"status": "DOWNLOAD_MODE_INDICATED", "action": "NONE", "reason": "Text suggests ROM download mode; verify chip and wiring locally"}
    if chip == "esp32-wroom-32" and BOOT.search(obs):
        return {"status": "BOOT_LOG_OBSERVED", "action": "NONE", "reason": "Classic ESP32 boot field observed; strap interpretation needs board documentation"}
    return {"status": "INCONCLUSIVE", "action": "NONE", "reason": "Text does not establish boot mode or device identity"}

class Tests(unittest.TestCase):
    def test_download(self):
        self.assertEqual(classify({"chip": "esp32-wroom-32", "observation": "waiting for download"})["status"], "DOWNLOAD_MODE_INDICATED")
    def test_classic_boot(self):
        self.assertEqual(classify({"chip": "esp32-wroom-32", "observation": "rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)"})["status"], "BOOT_LOG_OBSERVED")
    def test_s2_not_assumed_classic(self):
        self.assertEqual(classify({"chip": "esp32-s2", "observation": "boot:0x13"})["status"], "INCONCLUSIVE")
    def test_no_text(self):
        self.assertEqual(classify({"chip": "esp32-s2", "observation": ""})["status"], "INVALID")
    def test_unknown_chip(self):
        self.assertEqual(classify({"chip": "esp32-c3", "observation": "waiting for download"})["status"], "INVALID")
    def test_fail_closed(self):
        for record in ([], {}, {"chip": "esp32-s2", "observation": "ok", "flash": True}):
            self.assertEqual(classify(record)["action"], "NONE")
    def test_bounded(self):
        self.assertEqual(classify({"chip": "esp32-s2", "observation": "x" * 4097})["status"], "INVALID")

    def test_usb_uart_parenthesized_token(self):
        self.assertEqual(classify({"chip": "esp32-s2", "observation": "mode: DOWNLOAD(USB/UART0)"})["status"], "DOWNLOAD_MODE_INDICATED")
    def test_reject_embedded_mode_token(self):
        self.assertEqual(classify({"chip": "esp32-s2", "observation": "NOT_DOWNLOAD(USB/UART0)ISH"})["status"], "INCONCLUSIVE")
    def test_download_boot_token(self):
        self.assertEqual(classify({"chip": "esp32-wroom-32", "observation": "boot:0x3 (DOWNLOAD_BOOT)"})["status"], "DOWNLOAD_MODE_INDICATED")

def main():
    p = argparse.ArgumentParser(description="Offline ESP32 ROM log classifier (never flashes)")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--chip", choices=sorted(CHIPS))
    p.add_argument("--observation")
    a = p.parse_args()
    if a.self_test:
        unittest.main(argv=["self-test"], exit=False)
    else:
        print(json.dumps(classify({"chip": a.chip, "observation": a.observation}), sort_keys=True))

if __name__ == "__main__":
    main()
