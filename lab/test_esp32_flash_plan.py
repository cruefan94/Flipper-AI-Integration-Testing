import unittest
from esp32_flash_plan import plan

class FlashPlanTests(unittest.TestCase):
    def test_wroom(self):
        p = plan('esp32', '/dev/ttyUSB0')
        self.assertFalse(p['executed'])
        self.assertEqual(p['preview_argv'][-1], 'chip_id')
    def test_s2(self):
        self.assertEqual(plan('esp32s2', '/dev/ttyACM1')['chip'], 'esp32s2')
    def test_stable_alias(self):
        self.assertEqual(plan('esp32', '/dev/serial/by-id/usb-Silicon_Labs_CP2102_123-if00-port0')['baud'], 115200)
    def test_reject_shell(self):
        for value in ['/dev/ttyUSB0;reboot', '../../dev/ttyUSB0', '/tmp/fake', '/dev/ttyUSB0\nfoo']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                plan('esp32', value)
    def test_reject_wrong_chip(self):
        with self.assertRaises(ValueError):
            plan('auto', '/dev/ttyUSB0')
    def test_reject_baud(self):
        with self.assertRaises(ValueError):
            plan('esp32', '/dev/ttyUSB0', 12345)

if __name__ == '__main__':
    unittest.main()
