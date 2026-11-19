"""Offline, fail-closed power-domain preflight for modular Flipper backpacks.

Public-safe synthetic fixtures only. No GPIO, USB, serial, network or flash I/O.
This is a screening aid, NOT an electrical certification.
"""
from dataclasses import dataclass
import unittest

@dataclass(frozen=True)
class Link:
    source: str
    target: str
    kind: str
    source_voltage: float
    target_max_voltage: float
    level_shifted: bool = False

ALLOWED = {"flipper", "esp32_wroom", "esp32_s2", "arduino_uno", "sensor"}

def validate(links, *, common_ground_verified=False, independent_power_verified=False):
    errors = []
    if not links:
        return ["empty wiring manifest"]
    if not common_ground_verified:
        errors.append("common ground not verified")
    if not independent_power_verified:
        errors.append("power-source isolation not verified")
    for i, link in enumerate(links):
        prefix = f"link {i}: "
        if link.source not in ALLOWED or link.target not in ALLOWED:
            errors.append(prefix + "unknown device")
        if link.kind not in {"signal", "ground"}:
            errors.append(prefix + "power rails are not approved for direct interconnect")
            continue
        if link.source == link.target:
            errors.append(prefix + "self connection")
        if link.kind == "signal":
            if not (0 <= link.source_voltage <= 5.5 and 0 < link.target_max_voltage <= 5.5):
                errors.append(prefix + "voltage out of supported screening range")
            elif link.source_voltage > link.target_max_voltage and not link.level_shifted:
                errors.append(prefix + "overvoltage without level shifting")
            if link.source_voltage > link.target_max_voltage and link.level_shifted:
                # Level-shifter selection, wiring and power remain subject to physical verification.
                pass
    return errors

class TestBackpackPreflight(unittest.TestCase):
    def setUp(self):
        self.safe = [Link("esp32_wroom", "flipper", "signal", 3.3, 3.3)]
        self.flags = dict(common_ground_verified=True, independent_power_verified=True)

    def test_safe_signal(self):
        self.assertEqual(validate(self.safe, **self.flags), [])
    def test_no_ground_evidence(self):
        self.assertIn("common ground not verified", validate(self.safe, independent_power_verified=True))
    def test_no_power_isolation(self):
        self.assertIn("power-source isolation not verified", validate(self.safe, common_ground_verified=True))
    def test_5v_to_3v3_rejected(self):
        self.assertTrue(any("overvoltage" in x for x in validate([Link("arduino_uno", "esp32_wroom", "signal", 5.0, 3.3)], **self.flags)))
    def test_level_shifter_screening(self):
        self.assertEqual(validate([Link("arduino_uno", "esp32_wroom", "signal", 5.0, 3.3, True)], **self.flags), [])
    def test_direct_power_rail_rejected(self):
        self.assertTrue(any("power rails" in x for x in validate([Link("arduino_uno", "flipper", "power", 5, 3.3)], **self.flags)))
    def test_unknown_device(self):
        self.assertTrue(any("unknown" in x for x in validate([Link("mystery", "flipper", "signal", 3.3, 3.3)], **self.flags)))
    def test_empty_manifest(self):
        self.assertEqual(validate([], **self.flags), ["empty wiring manifest"])
    def test_negative_voltage(self):
        self.assertTrue(any("voltage out" in x for x in validate([Link("sensor", "flipper", "signal", -1, 3.3)], **self.flags)))

if __name__ == "__main__":
    unittest.main()
