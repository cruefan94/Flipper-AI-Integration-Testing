"""Offline ESP32 Pi-side serial preflight. Never opens ports or runs esptool.

Inputs are manually collected observations; no hardware detection is implied.
"""
from dataclasses import dataclass
import re
import unittest

PORT = re.compile(r"^/dev/(ttyUSB[0-9]{1,3}|ttyACM[0-9]{1,3})$")
CHIPS = {"esp32", "esp32s2"}

@dataclass(frozen=True)
class Observation:
    chip: str
    port: str
    usb_visible: bool
    serial_visible: bool
    ground_verified: bool
    logic_3v3_verified: bool
    manual_download_mode: bool
    power_stable: bool
    competing_process: bool = False

def evaluate(o: Observation) -> dict:
    """Return fail-closed advisory, not flash permission."""
    problems = []
    if o.chip not in CHIPS:
        problems.append("unknown_chip")
    if not isinstance(o.port, str) or not PORT.fullmatch(o.port):
        problems.append("invalid_port")
    for field in ("usb_visible", "serial_visible", "ground_verified",
                  "logic_3v3_verified", "manual_download_mode", "power_stable",
                  "competing_process"):
        if type(getattr(o, field)) is not bool:
            problems.append("invalid_" + field)
    if o.usb_visible is not True:
        problems.append("usb_not_observed")
    if o.serial_visible is not True:
        problems.append("serial_not_observed")
    if o.ground_verified is not True:
        problems.append("ground_unverified")
    if o.logic_3v3_verified is not True:
        problems.append("logic_voltage_unverified")
    if o.manual_download_mode is not True:
        problems.append("download_mode_unverified")
    if o.power_stable is not True:
        problems.append("power_unverified")
    if o.competing_process is not False:
        problems.append("port_busy_or_unknown")
    return {"status": "OBSERVATIONS_COMPLETE_NOT_HARDWARE_VERIFIED" if not problems else "BLOCKED",
            "problems": problems, "flash_authorized": False,
            "port_opened": False, "esptool_executed": False}

class Tests(unittest.TestCase):
    def good(self, **kw):
        d = dict(chip="esp32", port="/dev/ttyUSB0", usb_visible=True,
                 serial_visible=True, ground_verified=True,
                 logic_3v3_verified=True, manual_download_mode=True,
                 power_stable=True, competing_process=False)
        d.update(kw)
        return Observation(**d)
    def test_observations_complete_still_not_authorized(self):
        r = evaluate(self.good())
        self.assertEqual(r["status"], "OBSERVATIONS_COMPLETE_NOT_HARDWARE_VERIFIED")
        self.assertFalse(r["flash_authorized"])
    def test_s2(self):
        self.assertEqual(evaluate(self.good(chip="esp32s2", port="/dev/ttyACM1"))["problems"], [])
    def test_invalid_chip(self):
        self.assertIn("unknown_chip", evaluate(self.good(chip="esp32c3"))["problems"])
    def test_port_injection(self):
        self.assertIn("invalid_port", evaluate(self.good(port="/dev/ttyUSB0; echo unsafe"))["problems"])
    def test_non_serial_device(self):
        self.assertIn("invalid_port", evaluate(self.good(port="/dev/sda"))["problems"])
    def test_missing_usb(self):
        self.assertIn("usb_not_observed", evaluate(self.good(usb_visible=False))["problems"])
    def test_missing_serial(self):
        self.assertIn("serial_not_observed", evaluate(self.good(serial_visible=False))["problems"])
    def test_unsafe_voltage(self):
        self.assertIn("logic_voltage_unverified", evaluate(self.good(logic_3v3_verified=False))["problems"])
    def test_ground(self):
        self.assertIn("ground_unverified", evaluate(self.good(ground_verified=False))["problems"])
    def test_boot_mode(self):
        self.assertIn("download_mode_unverified", evaluate(self.good(manual_download_mode=False))["problems"])
    def test_unstable_power(self):
        self.assertIn("power_unverified", evaluate(self.good(power_stable=False))["problems"])
    def test_port_busy(self):
        self.assertIn("port_busy_or_unknown", evaluate(self.good(competing_process=True))["problems"])
    def test_wrong_boolean_type(self):
        self.assertIn("invalid_usb_visible", evaluate(self.good(usb_visible="yes"))["problems"])
    def test_never_opens_hardware(self):
        r = evaluate(self.good())
        self.assertFalse(r["port_opened"])
        self.assertFalse(r["esptool_executed"])

if __name__ == "__main__":
    unittest.main()
