import unittest
from flash_plan import validate

BASE = dict(chip='esp32', observed_chip='esp32', port='/dev/serial/by-id/usb-CP2102_ABC', operation='review-only', common_ground_verified=True, uart_voltage_v=3.3, image_sha256='a'*64, board_identity_verified=True)

class FlashPlanTests(unittest.TestCase):
    def test_valid_review(self): self.assertEqual(validate(BASE), [])
    def test_s2(self):
        p = dict(BASE, chip='esp32s2', observed_chip='esp32s2'); self.assertEqual(validate(p), [])
    def test_mismatch(self): self.assertIn('observed chip mismatch', validate(dict(BASE, observed_chip='esp32s2')))
    def test_unstable_port(self): self.assertIn('stable by-id port required', validate(dict(BASE, port='/dev/ttyUSB0')))
    def test_command_block(self): self.assertIn('only review-only operation allowed', validate(dict(BASE, operation='write_flash')))
    def test_voltage(self): self.assertIn('invalid UART voltage', validate(dict(BASE, uart_voltage_v=5)))
    def test_nan(self): self.assertIn('invalid UART voltage', validate(dict(BASE, uart_voltage_v=float('nan'))))
    def test_boolean_voltage(self): self.assertIn('invalid UART voltage', validate(dict(BASE, uart_voltage_v=True)))
    def test_digest(self): self.assertIn('invalid image digest', validate(dict(BASE, image_sha256='bad')))
    def test_ground(self): self.assertIn('common ground unverified', validate(dict(BASE, common_ground_verified=False)))
    def test_identity(self): self.assertIn('board identity unverified', validate(dict(BASE, board_identity_verified=False)))
    def test_invalid_object(self): self.assertTrue(validate(None))

if __name__ == '__main__': unittest.main()
