import unittest
from pi_esp32_boot_trace_gate import classify

BASE = {'board_label':'ESP32 WROOM development board', 'usb_vid_pid':'10c4:ea60', 'boot_held_low':True, 'en_reset_observed':True, 'reported_mode':'download'}
class BootGateTests(unittest.TestCase):
    def test_consistent(self):
        self.assertEqual(classify(BASE)['status'], 'consistent_download_observation')
    def test_never_authorizes(self):
        self.assertFalse(classify(BASE)['flash_authorized'])
        self.assertFalse(classify(BASE)['board_identity_verified'])
    def test_missing_observation(self):
        self.assertEqual(classify({**BASE,'en_reset_observed':False})['status'],'inconsistent_download_observation')
    def test_normal_mode(self):
        self.assertEqual(classify({**BASE,'reported_mode':'normal'})['status'],'insufficient_download_evidence')
    def test_bad_types(self):
        for value in (1,'true',None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                classify({**BASE,'boot_held_low':value})
    def test_bad_usb(self):
        with self.assertRaises(ValueError): classify({**BASE,'usb_vid_pid':'/dev/ttyUSB0'})
    def test_extra_field(self):
        with self.assertRaises(ValueError): classify({**BASE,'flash':True})
    def test_invalid_mode(self):
        with self.assertRaises(ValueError): classify({**BASE,'reported_mode':'flash'})
    def test_non_object(self):
        with self.assertRaises(ValueError): classify([])
if __name__ == '__main__': unittest.main()
