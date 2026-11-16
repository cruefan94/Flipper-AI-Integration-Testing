"""Synthetic, hardware-free checks for Pi ESP32 preflight."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    'esp32_preflight', Path(__file__).with_name('esp32_preflight.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ReadOnlyPreflightTests(unittest.TestCase):
    def test_port_classes(self):
        self.assertIn('USB-UART', mod.classify_port('/dev/ttyUSB0'))
        self.assertIn('onboard UART', mod.classify_port('/dev/ttyAMA0'))
        self.assertIn('persistent', mod.classify_port('/dev/serial/by-id/usb-device'))

    def test_missing_port_never_claims_flash_ready(self):
        info = mod.inspect_port('/dev/does-not-exist-flipper-lab')
        self.assertFalse(info['exists'])
        self.assertFalse(info['safe_to_flash'])

    def test_report_is_diagnostic_only(self):
        result = mod.report(['/dev/does-not-exist-flipper-lab'])
        self.assertEqual(result['mode'], 'read_only_preflight')
        self.assertFalse(result['ports'][0]['safe_to_flash'])
        self.assertTrue(any('No flashing' in note for note in result['notes']))


if __name__ == '__main__':
    unittest.main()
