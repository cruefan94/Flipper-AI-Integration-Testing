import unittest
from serial_port_preflight import review

GOOD = {'port': '/dev/ttyUSB0', 'board': 'esp32-wroom', 'serial': 'LAB-01'}

class TestPreflight(unittest.TestCase):
    def test_valid_review_only(self): self.assertEqual(review([GOOD])['status'], 'REVIEW_ONLY')
    def test_empty(self): self.assertEqual(review([])['status'], 'BLOCKED')
    def test_bad_port(self): self.assertEqual(review([{**GOOD, 'port': '/dev/ttyS0'}])['status'], 'BLOCKED')
    def test_duplicate_port(self): self.assertIn('1:duplicate_port', review([GOOD, {**GOOD, 'serial': 'LAB-02'}])['reasons'])
    def test_duplicate_identity(self): self.assertIn('1:duplicate_identity', review([GOOD, {**GOOD, 'port': '/dev/ttyUSB1'}])['reasons'])
    def test_unknown_serial(self): self.assertEqual(review([{**GOOD, 'serial': 'unknown'}])['status'], 'BLOCKED')
    def test_unsupported_board(self): self.assertEqual(review([{**GOOD, 'board': 'mystery'}])['status'], 'BLOCKED')
    def test_invalid_record(self): self.assertEqual(review([None])['status'], 'BLOCKED')
    def test_two_boards(self): self.assertEqual(review([GOOD, {'port':'/dev/ttyACM0','board':'flipper-zero','serial':'LAB-02'}])['status'], 'REVIEW_ONLY')
    def test_no_flash_authorization(self): self.assertNotIn('AUTHORIZED', str(review([GOOD])))

if __name__ == '__main__': unittest.main()
