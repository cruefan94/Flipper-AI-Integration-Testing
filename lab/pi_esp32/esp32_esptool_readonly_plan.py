"""Offline ESP32 read-only esptool command planner; never accesses hardware."""
import argparse
import json
import re
import unittest

PORT_RE = re.compile(r"^/dev/(ttyUSB[0-9]{1,3}|ttyACM[0-9]{1,3}|serial/by-id/[A-Za-z0-9_.:-]{1,120})$")
CHIPS = {"esp32", "esp32s2"}

def plan(chip: str, port: str, baud: int = 115200) -> dict:
    if chip not in CHIPS:
        raise ValueError("unsupported chip")
    if not isinstance(port, str) or not PORT_RE.fullmatch(port) or ".." in port:
        raise ValueError("invalid local serial path")
    if type(baud) is not int or baud not in (9600, 57600, 115200):
        raise ValueError("unsupported baud rate")
    return {
        "status": "PLAN_ONLY_NO_EXECUTION",
        "chip": chip,
        "argv": ["python3", "-m", "esptool", "--chip", chip, "--port", port,
                 "--baud", str(baud), "--before", "no-reset", "--after", "no-reset", "chip_id"],
        "requirements": ["Owner confirms board and port", "Verify 3.3V logic and shared ground",
                         "Manually enter ROM bootloader", "Execute locally only after owner approval"],
    }

class PlanTests(unittest.TestCase):
    def test_wroom(self):
        self.assertEqual(plan("esp32", "/dev/ttyUSB0")["chip"], "esp32")
    def test_s2(self):
        self.assertEqual(plan("esp32s2", "/dev/ttyACM1")["chip"], "esp32s2")
    def test_by_id(self):
        self.assertIn("chip_id", plan("esp32", "/dev/serial/by-id/usb-Silicon_Labs_CP2102")["argv"])
    def test_reject_paths(self):
        for port in ("/dev/ttyS0", "socket://host:123", "/dev/ttyUSB0;echo hi", "../../ttyUSB0", "/dev/serial/by-id/../x"):
            with self.subTest(port=port), self.assertRaises(ValueError):
                plan("esp32", port)
    def test_reject_chips(self):
        for chip in ("auto", "esp32c3", "ESP32", "esp32 --force"):
            with self.subTest(chip=chip), self.assertRaises(ValueError):
                plan(chip, "/dev/ttyUSB0")
    def test_reject_baud(self):
        for baud in (0, 921600, "115200", True):
            with self.subTest(baud=baud), self.assertRaises(ValueError):
                plan("esp32", "/dev/ttyUSB0", baud)
    def test_never_flash(self):
        cmd = " ".join(plan("esp32", "/dev/ttyUSB0")["argv"])
        self.assertNotIn("write_flash", cmd)
        self.assertNotIn("erase_flash", cmd)
        self.assertIn("no-reset", cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chip", choices=sorted(CHIPS), required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--baud", type=int, default=115200)
    args = parser.parse_args()
    print(json.dumps(plan(args.chip, args.port, args.baud), indent=2))
