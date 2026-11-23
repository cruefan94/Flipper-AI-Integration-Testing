import unittest
from pi_usb_snapshot import validate

class TestSnapshot(unittest.TestCase):
    def setUp(self):
        self.row = {'port':'/dev/ttyUSB0','vid':'10C4','pid':'EA60','operator_label':'WROOM candidate'}
    def test_valid_not_authorized(self):
        result=validate({'observations':[self.row]})
        self.assertFalse(result['flash_authorized'])
        self.assertFalse(result['observations'][0]['identity_verified'])
    def test_empty(self):
        self.assertFalse(validate({'observations':[]})['flash_authorized'])
    def test_duplicate(self):
        with self.assertRaises(ValueError): validate({'observations':[self.row,self.row]})
    def test_alias(self):
        with self.assertRaises(ValueError): validate({'observations':[{**self.row,'port':'/dev/ttyUSB00'}]})
    def test_injection(self):
        with self.assertRaises(ValueError): validate({'observations':[{**self.row,'port':'/dev/ttyUSB0;echo x'}]})
    def test_extra_fields(self):
        with self.assertRaises(ValueError): validate({'observations':[{**self.row,'flash_authorized':True}]})
    def test_invalid_hex(self):
        with self.assertRaises(ValueError): validate({'observations':[{**self.row,'vid':'FFFFF'}]})
    def test_limit(self):
        with self.assertRaises(ValueError): validate({'observations':[self.row]*17})
    def test_bad_label(self):
        with self.assertRaises(ValueError): validate({'observations':[{**self.row,'operator_label':'  '}]})
    def test_boolean_not_port(self):
        with self.assertRaises(ValueError): validate({'observations':[{**self.row,'port':True}]})

if __name__=='__main__': unittest.main()
