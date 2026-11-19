"""Offline digital logic-level preflight for Arduino Uno, Flipper and ESP32.
No GPIO access, hardware operations, or external dependencies.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Pin:
    board: str
    signal: str
    voltage: float
    direction: str

SUPPORTED = {'uno', 'flipper', 'esp32-wroom', 'esp32-s2'}

def assess(a: Pin, b: Pin, *, level_shifter=False, common_ground=False):
    """Conservative proposal check. Does not validate pinout, power or loads."""
    for p in (a, b):
        if p.board not in SUPPORTED or p.direction not in ('in', 'out'):
            return False, 'unsupported board or direction'
        if p.signal not in ('digital', 'uart'):
            return False, 'unsupported signal type; manual review required'
        if p.voltage not in (3.3, 5.0):
            return False, 'unsupported logic voltage'
        if p.board != 'uno' and p.voltage != 3.3:
            return False, '3.3V device declared at incorrect logic voltage'
        if p.board == 'uno' and p.voltage != 5.0:
            return False, 'Uno digital pin declared at incorrect logic voltage'
    if a.board == b.board:
        return False, 'same-board wiring requires separate review'
    if not common_ground:
        return False, 'common ground not confirmed'
    if a.direction == b.direction:
        return False, 'must connect one output to one input'
    source, sink = (a, b) if a.direction == 'out' else (b, a)
    if source.voltage > sink.voltage and not level_shifter:
        return False, '5V output to 3.3V input: level shifting required'
    if source.voltage < sink.voltage:
        return False, '3.3V output to 5V input: input-high compatibility unverified'
    return True, 'limited offline logic-level checks passed; verify pinout and power separately'

if __name__ == '__main__':
    import unittest
    class SafetyTests(unittest.TestCase):
        def test_uno_to_flipper_rejected(self):
            self.assertFalse(assess(Pin('uno','digital',5,'out'), Pin('flipper','digital',3.3,'in'), common_ground=True)[0])
        def test_uno_to_flipper_shifted(self):
            self.assertTrue(assess(Pin('uno','digital',5,'out'), Pin('flipper','digital',3.3,'in'), level_shifter=True, common_ground=True)[0])
        def test_uno_to_esp32_rejected(self):
            self.assertFalse(assess(Pin('uno','uart',5,'out'), Pin('esp32-wroom','uart',3.3,'in'), common_ground=True)[0])
        def test_esp32_to_uno_unverified(self):
            self.assertFalse(assess(Pin('esp32-s2','uart',3.3,'out'), Pin('uno','uart',5,'in'), common_ground=True)[0])
        def test_two_outputs(self):
            self.assertFalse(assess(Pin('uno','digital',5,'out'), Pin('flipper','digital',3.3,'out'), common_ground=True)[0])
        def test_missing_ground(self):
            self.assertFalse(assess(Pin('esp32-wroom','digital',3.3,'out'), Pin('flipper','digital',3.3,'in'))[0])
        def test_3v3_connection(self):
            self.assertTrue(assess(Pin('esp32-wroom','digital',3.3,'out'), Pin('flipper','digital',3.3,'in'), common_ground=True)[0])
        def test_unknown_board(self):
            self.assertFalse(assess(Pin('unknown','digital',3.3,'out'), Pin('flipper','digital',3.3,'in'), common_ground=True)[0])
        def test_power_pin_rejected(self):
            self.assertFalse(assess(Pin('uno','power',5,'out'), Pin('flipper','power',3.3,'in'), common_ground=True)[0])
    unittest.main()
