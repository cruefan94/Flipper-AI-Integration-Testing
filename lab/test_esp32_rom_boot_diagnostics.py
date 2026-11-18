import unittest
from lab.esp32_rom_boot_diagnostics import diagnose

class BootTests(unittest.TestCase):
    def test_download(self):
        self.assertEqual(diagnose('rst:0x1,boot:0x3 (DOWNLOAD_BOOT(UART0/UART1/SDIO_REI_REO_V2))')['status'], 'download')
    def test_flash(self):
        self.assertEqual(diagnose('rst:0x1,boot:0x13 (SPI_FAST_FLASH_BOOT)')['status'], 'flash')
    def test_missing(self):
        self.assertEqual(diagnose('nothing')['status'], 'unknown')
    def test_invalid(self):
        self.assertEqual(diagnose(None)['status'], 'invalid')
    def test_last_reset(self):
        self.assertEqual(diagnose('boot:0x13 (SPI_FAST_FLASH_BOOT)\nboot:0x3 (DOWNLOAD_BOOT(UART0/UART1/SDIO_REI_REO_V2))')['status'], 'download')

if __name__ == '__main__': unittest.main()
