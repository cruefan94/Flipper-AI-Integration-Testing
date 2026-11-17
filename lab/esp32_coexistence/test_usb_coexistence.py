import unittest
from usb_coexistence import review

A = {'board':'esp32-wroom','port':'/dev/serial/by-id/wroom','serial':'A'}
B = {'board':'esp32-s2','port':'/dev/serial/by-id/s2','serial':'B'}
class CoexistenceTests(unittest.TestCase):
    def test_two_boards(self): self.assertTrue(review([A,B])['ok'])
    def test_no_flash(self): self.assertFalse(review([A,B])['flash_authorized'])
    def test_empty(self): self.assertFalse(review([])['ok'])
    def test_bad_record(self): self.assertFalse(review([None])['ok'])
    def test_unknown_board(self): self.assertFalse(review([A|{'board':'unknown'}])['ok'])
    def test_unstable_port(self): self.assertFalse(review([A|{'port':'/dev/ttyUSB0'}])['ok'])
    def test_duplicate_port(self): self.assertIn('duplicate_port',review([A,B|{'port':A['port']}])['errors'])
    def test_duplicate_identity(self): self.assertIn('duplicate_identity',review([A,A|{'port':B['port']}])['errors'])
    def test_unknown_serial(self): self.assertFalse(review([A|{'serial':'unknown'}])['ok'])
    def test_same_serial_different_board(self): self.assertTrue(review([A,B|{'serial':'A'}])['ok'])
if __name__ == '__main__': unittest.main()
