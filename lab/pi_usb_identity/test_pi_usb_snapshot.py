import unittest
from pi_usb_snapshot import Observation, evaluate

class Tests(unittest.TestCase):
    def setUp(self):
        self.a = Observation('/dev/ttyUSB0', '10c4', 'ea60', 'SER-A')
        self.b = Observation('/dev/ttyACM0', '0483', '5740', 'SER-B')
    def test_valid_still_review(self): self.assertEqual(evaluate([self.a], self.a.port)[0], 'REVIEW')
    def test_no_data(self): self.assertEqual(evaluate([], self.a.port)[0], 'DENY')
    def test_missing_port(self): self.assertEqual(evaluate([self.a], self.b.port)[0], 'DENY')
    def test_duplicate_port(self): self.assertEqual(evaluate([self.a,self.a], self.a.port)[0], 'DENY')
    def test_collision(self): self.assertEqual(evaluate([self.a, Observation(self.b.port,'0483','5740','SER-A')], self.a.port)[0], 'DENY')
    def test_missing_serial(self): self.assertEqual(evaluate([Observation(self.a.port,'10c4','ea60')], self.a.port)[0], 'REVIEW')
    def test_bad_vid(self): self.assertEqual(evaluate([Observation(self.a.port,'ZZZZ','ea60','SER-A')], self.a.port)[0], 'DENY')
    def test_path_injection(self): self.assertEqual(evaluate([self.a], '/dev/ttyUSB0;echo')[0], 'DENY')

if __name__ == '__main__': unittest.main()
