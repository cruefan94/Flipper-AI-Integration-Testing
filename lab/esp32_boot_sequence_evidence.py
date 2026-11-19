"""Offline ESP32 strap/reset evidence checks. Never opens a port or drives GPIO."""
from dataclasses import dataclass
from typing import Sequence
import unittest

@dataclass(frozen=True)
class Observation:
    phase: str
    gpio0_low: bool
    en_high: bool
    voltage_ok: bool
    ground_verified: bool

def assess_boot_sequence(samples: Sequence[Observation], chip: str) -> tuple[bool, str]:
    """Fail closed unless a documented reset-to-ROM sequence is observed."""
    if chip not in ("ESP32", "ESP32-S2"):
        return False, "unsupported chip family"
    if len(samples) != 3:
        return False, "expected exactly three observations"
    if tuple(s.phase for s in samples) != ("hold", "reset", "release"):
        return False, "invalid phase order"
    if not all(s.voltage_ok and s.ground_verified for s in samples):
        return False, "electrical verification missing"
    hold, reset, release = samples
    if not (hold.gpio0_low and hold.en_high):
        return False, "GPIO0 must be held low before reset"
    if not (reset.gpio0_low and not reset.en_high):
        return False, "EN must be asserted low while GPIO0 stays low"
    if not (release.gpio0_low and release.en_high):
        return False, "EN must be released while GPIO0 remains low"
    return True, "strap/reset observations consistent; ROM handshake still required"

def good():
    return [Observation("hold", True, True, True, True),
            Observation("reset", True, False, True, True),
            Observation("release", True, True, True, True)]

class BootEvidenceTests(unittest.TestCase):
    def test_esp32(self): self.assertTrue(assess_boot_sequence(good(), "ESP32")[0])
    def test_s2(self): self.assertTrue(assess_boot_sequence(good(), "ESP32-S2")[0])
    def test_unknown(self): self.assertFalse(assess_boot_sequence(good(), "ESP32-C6")[0])
    def test_missing_sample(self): self.assertFalse(assess_boot_sequence(good()[:2], "ESP32")[0])
    def test_reordered(self):
        s = good()
        self.assertFalse(assess_boot_sequence([s[1], s[0], s[2]], "ESP32")[0])
    def test_no_ground(self):
        s = good(); s[1] = Observation("reset", True, False, True, False)
        self.assertFalse(assess_boot_sequence(s, "ESP32")[0])
    def test_voltage_unverified(self):
        s = good(); s[0] = Observation("hold", True, True, False, True)
        self.assertFalse(assess_boot_sequence(s, "ESP32")[0])
    def test_gpio0_released_too_early(self):
        s = good(); s[2] = Observation("release", False, True, True, True)
        self.assertFalse(assess_boot_sequence(s, "ESP32")[0])
    def test_en_not_reset(self):
        s = good(); s[1] = Observation("reset", True, True, True, True)
        self.assertFalse(assess_boot_sequence(s, "ESP32")[0])

if __name__ == "__main__":
    unittest.main()
