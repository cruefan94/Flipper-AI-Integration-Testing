"""Offline-only ESP32 ROM chip-ID command planner; never executes commands."""
import argparse
import json
import re
import unittest

PORT = re.compile(r"^/dev/(ttyUSB[0-9]+|ttyACM[0-9]+|serial/by-id/[A-Za-z0-9_.:+-]+)$")
CHIPS = {"esp32": "ESP32-WROOM class", "esp32s2": "ESP32-S2 separate BOOT/USB procedure"}

def plan(chip, port, logic_voltage, power_verified):
    errors = []
    if chip not in CHIPS:
        errors.append("Unsupported chip; verify marking")
    if not PORT.fullmatch(port):
        errors.append("Unsupported port path")
    if logic_voltage != 3.3:
        errors.append("Verify 3.3V TX/RX logic")
    if power_verified is not True:
        errors.append("Verify board power and common ground")
    return {
        "ready_for_owner_review": not errors,
        "errors": errors,
        "chip": CHIPS.get(chip, "unknown"),
        "command_argv": ["python3", "-m", "esptool", "--chip", chip,
                         "--port", port, "chip_id"] if not errors else None,
        "warning": "PLAN ONLY. Never auto-execute. chip_id may toggle DTR/RTS; verify reset wiring before owner runs it. No flashing."
    }

class Tests(unittest.TestCase):
    def test_usb(self):
        self.assertTrue(plan("esp32", "/dev/ttyUSB0", 3.3, True)["ready_for_owner_review"])
    def test_acm(self):
        self.assertTrue(plan("esp32s2", "/dev/ttyACM2", 3.3, True)["ready_for_owner_review"])
    def test_byid(self):
        self.assertTrue(plan("esp32", "/dev/serial/by-id/usb-CP2102_123", 3.3, True)["ready_for_owner_review"])
    def test_5v(self):
        self.assertFalse(plan("esp32", "/dev/ttyUSB0", 5, True)["ready_for_owner_review"])
    def test_power(self):
        self.assertFalse(plan("esp32", "/dev/ttyUSB0", 3.3, False)["ready_for_owner_review"])
    def test_chip(self):
        self.assertFalse(plan("esp32s3", "/dev/ttyUSB0", 3.3, True)["ready_for_owner_review"])
    def test_path(self):
        self.assertIsNone(plan("esp32", "/dev/ttyUSB0;echo BAD", 3.3, True)["command_argv"])
    def test_no_flash(self):
        self.assertNotIn("write_flash", str(plan("esp32", "/dev/ttyUSB0", 3.3, True)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--chip")
    parser.add_argument("--port")
    parser.add_argument("--logic-voltage", type=float)
    parser.add_argument("--power-verified", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["offline-tests"], exit=False)
    else:
        print(json.dumps(plan(args.chip, args.port or "", args.logic_voltage,
                              args.power_verified), indent=2))
