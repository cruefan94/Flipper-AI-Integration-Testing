import unittest
from esp32_reset_sequence import validate

class SequenceTests(unittest.TestCase):
    def test_good_wroom(self):
        self.assertTrue(validate({'chip':'wroom','events':[{'pin':'BOOT','level':0},{'pin':'EN','level':0},{'pin':'EN','level':1} ]})['ok'])
    def test_good_s2(self):
        self.assertTrue(validate({'chip':'s2','events':[{'pin':'EN','level':0},{'pin':'BOOT','level':0},{'pin':'EN','level':1}]})['ok'])
    def test_no_boot(self):
        self.assertFalse(validate({'chip':'wroom','events':[{'pin':'EN','level':0},{'pin':'EN','level':1}]})['ok'])
    def test_wrong_order(self):
        self.assertFalse(validate({'chip':'wroom','events':[{'pin':'EN','level':0},{'pin':'EN','level':1},{'pin':'BOOT','level':0}]})['ok'])
    def test_invalid_pin(self):
        self.assertFalse(validate({'chip':'s2','events':[{'pin':'GPIO','level':0}]})['ok'])
    def test_boolean_level(self):
        self.assertFalse(validate({'chip':'s2','events':[{'pin':'BOOT','level':False}]})['ok'])
    def test_unknown_chip(self):
        self.assertFalse(validate({'chip':'c3','events':[]})['ok'])
    def test_bad_events(self):
        self.assertFalse(validate({'chip':'wroom','events':'BOOT LOW'})['ok'])

if __name__ == '__main__': unittest.main()
