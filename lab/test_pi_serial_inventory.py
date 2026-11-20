import unittest
from pi_serial_inventory import inspect_inventory

class InventoryTests(unittest.TestCase):
    def test_valid_candidate_still_not_authorized(self):
        result = inspect_inventory({'ports':[{'path':'/dev/ttyUSB0','vid':'10c4','pid':'ea60'}], 'usb_devices':[]})
        self.assertFalse(result['ready'])
        self.assertEqual(result['errors'], [])
        self.assertEqual(len(result['candidates']), 1)
    def test_missing_serial(self):
        self.assertIn('no serial candidates', inspect_inventory({'ports':[], 'usb_devices':[]})['errors'])
    def test_injection_path(self):
        self.assertIn('invalid port identity', inspect_inventory({'ports':[{'path':'/dev/ttyUSB0;rm -rf /','vid':'10c4','pid':'ea60'}], 'usb_devices':[]})['errors'])
    def test_duplicate(self):
        p={'path':'/dev/ttyACM0','vid':'303a','pid':'1001'}
        self.assertIn('duplicate serial port', inspect_inventory({'ports':[p,p], 'usb_devices':[]})['errors'])
    def test_bad_vid(self):
        self.assertIn('invalid port identity', inspect_inventory({'ports':[{'path':'/dev/ttyUSB1','vid':'xyz','pid':'0001'}], 'usb_devices':[]})['errors'])
    def test_schema(self):
        self.assertIn('invalid inventory schema', inspect_inventory({'ports':[]})['errors'])
    def test_non_list(self):
        self.assertIn('invalid inventory lists', inspect_inventory({'ports':'oops','usb_devices':[]})['errors'])
    def test_usb_record(self):
        self.assertIn('invalid USB record', inspect_inventory({'ports':[], 'usb_devices':[{'vid':'abc','pid':'1234'}]})['errors'])
    def test_never_ready(self):
        self.assertFalse(inspect_inventory({'ports':[{'path':'/dev/ttyUSB2','vid':'1a86','pid':'7523'}], 'usb_devices':[{'vid':'1a86','pid':'7523'}]})['ready'])

if __name__ == '__main__':
    unittest.main()
