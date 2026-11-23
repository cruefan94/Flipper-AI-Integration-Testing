"""Offline classic ESP32-WROOM EN/BOOT observation sequence preflight.

Pure validation of operator-authored records; never opens ports or controls GPIO.
This does not certify board wiring, chip identity or flashing readiness.
"""
import unittest

VALID = {"HIGH", "LOW"}
MAX_EVENTS = 32


def check_sequence(events):
    if not isinstance(events, list) or not (3 <= len(events) <= MAX_EVENTS):
        return False, "invalid event count"
    normalized = []
    for event in events:
        if not isinstance(event, dict) or set(event) != {"en", "boot"}:
            return False, "invalid event shape"
        en, boot = event["en"], event["boot"]
        if type(en) is not str or type(boot) is not str or en not in VALID or boot not in VALID:
            return False, "invalid logic level"
        normalized.append((en, boot))
    if normalized[0] != ("HIGH", "HIGH"):
        return False, "must start idle"
    # Classic ESP32 UART download entry: BOOT held low during EN reset,
    # EN then rises while BOOT remains low, then BOOT may be released.
    for i in range(1, len(normalized)-1):
        if normalized[i] == ("LOW", "LOW") and normalized[i+1] == ("HIGH", "LOW"):
            if any(en == "LOW" and boot == "HIGH" for en, boot in normalized):
                return False, "unsafe ambiguous reset state"
            return True, "candidate classic ESP32 download entry; unverified"
    return False, "no EN reset while BOOT held low"


class SequenceTests(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(check_sequence([{"en":"HIGH","boot":"HIGH"},{"en":"HIGH","boot":"LOW"},{"en":"LOW","boot":"LOW"},{"en":"HIGH","boot":"LOW"},{"en":"HIGH","boot":"HIGH"}])[0])
    def test_normal_boot(self):
        self.assertFalse(check_sequence([{"en":"HIGH","boot":"HIGH"},{"en":"LOW","boot":"HIGH"},{"en":"HIGH","boot":"HIGH"}])[0])
    def test_no_reset(self):
        self.assertFalse(check_sequence([{"en":"HIGH","boot":"HIGH"},{"en":"HIGH","boot":"LOW"},{"en":"HIGH","boot":"HIGH"}])[0])
    def test_wrong_start(self):
        self.assertFalse(check_sequence([{"en":"LOW","boot":"LOW"},{"en":"HIGH","boot":"LOW"},{"en":"HIGH","boot":"HIGH"}])[0])
    def test_malformed(self):
        self.assertFalse(check_sequence([{}, {}, {}])[0])
    def test_invalid_voltage_label(self):
        self.assertFalse(check_sequence([{"en":"HIGH","boot":"HIGH"},{"en":"LOW","boot":"LOW"},{"en":"HIGH","boot":"3.3V"}])[0])
    def test_bounded(self):
        self.assertFalse(check_sequence([{"en":"HIGH","boot":"HIGH"}]*33)[0])
    def test_ambiguous_reset(self):
        self.assertFalse(check_sequence([{"en":"HIGH","boot":"HIGH"},{"en":"LOW","boot":"HIGH"},{"en":"LOW","boot":"LOW"},{"en":"HIGH","boot":"LOW"}])[0])
    def test_not_list(self):
        self.assertFalse(check_sequence("HIGH LOW")[0])

if __name__ == "__main__":
    unittest.main()
