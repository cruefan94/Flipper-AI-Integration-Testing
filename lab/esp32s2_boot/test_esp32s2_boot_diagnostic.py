import unittest
from esp32s2_boot_diagnostic import classify

class BootLogTests(unittest.TestCase):
    def test_download(self): self.assertEqual(classify('rst:0x1 (POWERON),boot:0x0 (DOWNLOAD_BOOT)'), 'DOWNLOAD_MODE_INDICATED')
    def test_waiting(self): self.assertEqual(classify('waiting for download'), 'DOWNLOAD_MODE_INDICATED')
    def test_normal(self): self.assertEqual(classify('boot:0x13 (SPI_FAST_FLASH_BOOT)'), 'NORMAL_FLASH_BOOT_INDICATED')
    def test_empty(self): self.assertEqual(classify(''), 'NO_LOG')
    def test_unknown(self): self.assertEqual(classify('boot:0x07'), 'BOOT_MODE_UNKNOWN')
    def test_noise(self): self.assertEqual(classify('garbled serial bytes'), 'INCONCLUSIVE')
    def test_limit(self): self.assertEqual(classify('a'*65537), 'INVALID_LOG')
    def test_priority(self): self.assertEqual(classify('SPI_FAST_FLASH_BOOT\nwaiting for download'), 'DOWNLOAD_MODE_INDICATED')

if __name__ == '__main__': unittest.main()
