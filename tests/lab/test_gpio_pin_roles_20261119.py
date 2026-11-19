"""Public-safe offline board pin-role checks; not a wiring authorization."""
import unittest

# GPIO numbers are silicon GPIO labels, not physical header positions.
ESP32_WROOM_RESTRICTED = {0, 2, 4, 5, 12, 15}  # boot strapping; conservative
ESP32_WROOM_FLASH = set(range(6, 12))
ESP32_WROOM_INPUT_ONLY = {34, 35, 36, 39}
ESP32_S2_RESTRICTED = {0, 45, 46}  # boot straps; board dependent

def assess(board, gpio, direction, voltage, level_shifter=False):
    """Return (allowed, reason) for an abstract proposed digital signal."""
    if board not in {'esp32_wroom', 'esp32_s2', 'arduino_uno', 'flipper_zero'}:
        return False, 'unknown board'
    if type(gpio) is not int or gpio < 0:
        return False, 'invalid pin number'
    if direction not in {'input', 'output'}:
        return False, 'invalid direction'
    if type(voltage) not in (float, int) or isinstance(voltage, bool) or not (0 <= voltage <= 5.0):
        return False, 'invalid voltage'
    if board == 'esp32_wroom':
        if gpio not in set(range(0, 40)) - {20, 24, 28, 29, 30, 31}:
            return False, 'unavailable or unverified GPIO'
        if gpio in ESP32_WROOM_FLASH:
            return False, 'flash-connected GPIO'
        if gpio in ESP32_WROOM_RESTRICTED:
            return False, 'boot strapping GPIO requires board-specific review'
        if direction == 'output' and gpio in ESP32_WROOM_INPUT_ONLY:
            return False, 'input-only GPIO'
    elif board == 'esp32_s2':
        if gpio > 46 or gpio in {22, 23, 24, 25}:
            return False, 'unavailable or unverified GPIO'
        if gpio in ESP32_S2_RESTRICTED:
            return False, 'boot strapping GPIO requires board-specific review'
        if gpio in {19, 20}:
            return False, 'native USB pin requires board-specific review'
        if gpio in set(range(26, 33)):
            return False, 'possible flash/PSRAM connection requires board-specific review'
    elif board == 'arduino_uno':
        if gpio > 13:
            return False, 'only digital D0-D13 modeled'
        if gpio in {0, 1}:
            return False, 'UART programming pins reserved'
    else:
        return False, 'Flipper header pin mapping requires manual board review'
    if board.startswith('esp32') and voltage > 3.3:
        return False, 'overvoltage for ESP32 GPIO; shifter flag is not proof of safe voltage'
    return True, 'abstract pin check only; verify actual board schematic, supply, ground and wiring'

class PinRoleTests(unittest.TestCase):
    def test_wroom_flash(self): self.assertFalse(assess('esp32_wroom', 7, 'output', 3.3)[0])
    def test_wroom_strap(self): self.assertFalse(assess('esp32_wroom', 0, 'input', 3.3)[0])
    def test_wroom_input_only(self): self.assertFalse(assess('esp32_wroom', 34, 'output', 3.3)[0])
    def test_wroom_input_valid(self): self.assertTrue(assess('esp32_wroom', 34, 'input', 3.3)[0])
    def test_s2_usb(self): self.assertFalse(assess('esp32_s2', 19, 'output', 3.3)[0])
    def test_s2_flash(self): self.assertFalse(assess('esp32_s2', 26, 'output', 3.3)[0])
    def test_s2_strap(self): self.assertFalse(assess('esp32_s2', 45, 'input', 3.3)[0])
    def test_uno_uart(self): self.assertFalse(assess('arduino_uno', 1, 'output', 5.0)[0])
    def test_uno_digital(self): self.assertTrue(assess('arduino_uno', 8, 'output', 5.0)[0])
    def test_5v_esp32(self): self.assertFalse(assess('esp32_wroom', 18, 'input', 5.0, True)[0])
    def test_flipper_fail_closed(self): self.assertFalse(assess('flipper_zero', 1, 'output', 3.3)[0])
    def test_bool_pin_rejected(self): self.assertFalse(assess('esp32_s2', True, 'input', 3.3)[0])

if __name__ == '__main__':
    unittest.main()
