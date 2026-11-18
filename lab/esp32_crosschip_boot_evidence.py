"""Offline public-safe ESP32 ROM boot-log evidence classifier. Never opens devices."""
import re
import unittest

DOWNLOAD = re.compile(r'\b(?:DOWNLOAD_BOOT|DOWNLOAD\s*\(USB/UART0\)|DOWNLOAD\s*\(UART0\))', re.I)
SPI = re.compile(r'\bSPI_FAST_FLASH_BOOT\b', re.I)
BOOT = re.compile(r'\bboot\s*:\s*0x([0-9a-f]+)', re.I)

def classify(chip, log):
    if chip not in ('esp32', 'esp32-s2'):
        return {'status': 'unsupported', 'evidence': []}
    if not isinstance(log, str) or len(log) > 65536:
        return {'status': 'invalid', 'evidence': []}
    evidence = []
    for line in log.splitlines():
        if DOWNLOAD.search(line):
            evidence.append('download_rom_marker')
        if SPI.search(line):
            evidence.append('flash_rom_marker')
        match = BOOT.search(line)
        if match and chip == 'esp32':
            value = int(match.group(1), 16)
            if value == 0x3:
                evidence.append('esp32_download_strap')
            elif value == 0x13:
                evidence.append('esp32_flash_strap')
    evidence = sorted(set(evidence))
    download = any(e in evidence for e in ('download_rom_marker', 'esp32_download_strap'))
    flash = any(e in evidence for e in ('flash_rom_marker', 'esp32_flash_strap'))
    status = 'conflicting' if download and flash else 'download' if download else 'flash' if flash else 'inconclusive'
    return {'status': status, 'evidence': evidence}

class TestBootEvidence(unittest.TestCase):
    def test_wroom_download(self):
        self.assertEqual(classify('esp32', 'rst:0x1 (POWERON_RESET),boot:0x3 (DOWNLOAD_BOOT)')['status'], 'download')
    def test_wroom_flash(self):
        self.assertEqual(classify('esp32', 'boot:0x13 (SPI_FAST_FLASH_BOOT)')['status'], 'flash')
    def test_s2_download(self):
        self.assertEqual(classify('esp32-s2', 'boot:0x0 (DOWNLOAD(USB/UART0))')['status'], 'download')
    def test_s2_strap_not_assumed(self):
        self.assertEqual(classify('esp32-s2', 'boot:0x3')['status'], 'inconclusive')
    def test_conflicting_resets(self):
        self.assertEqual(classify('esp32', 'boot:0x3\nboot:0x13')['status'], 'conflicting')
    def test_empty(self):
        self.assertEqual(classify('esp32', '')['status'], 'inconclusive')
    def test_unsupported(self):
        self.assertEqual(classify('esp32-c3', 'DOWNLOAD_BOOT')['status'], 'unsupported')
    def test_oversize(self):
        self.assertEqual(classify('esp32', 'x'*65537)['status'], 'invalid')

if __name__ == '__main__':
    unittest.main()
