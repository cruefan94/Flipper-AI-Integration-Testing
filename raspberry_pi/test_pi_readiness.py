"""Synthetic, no-device tests for Raspberry Pi integration readiness."""
import tempfile
import unittest
from pathlib import Path

from raspberry_pi.pi_readiness import readiness


class PiReadinessTests(unittest.TestCase):
    def test_empty_tree_is_readonly_and_does_not_claim_hardware(self):
        with tempfile.TemporaryDirectory() as tmp:
            snap=readiness(Path(tmp)/"sys/class/tty",which=lambda _: None)
            self.assertTrue(snap["read_only"])
            self.assertEqual(snap["usb_serial_ports"],[])
            self.assertFalse(snap["qflipper_installed"])
            self.assertFalse(snap["verified_flipper_link"])
            self.assertFalse(snap["verified_esp32_link"])

    def test_synthetic_usb_labels_are_hints_not_verified_boards(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            tty=root/"sys/class/tty/ttyACM0"
            usb=root/"sys/devices/usb1"
            tty.mkdir(parents=True)
            usb.mkdir(parents=True)
            (tty/"device").symlink_to(usb, target_is_directory=True)
            (usb/"idVendor").write_text("0483",encoding="utf-8")
            (usb/"idProduct").write_text("5740",encoding="utf-8")
            (usb/"product").write_text("Flipper Zero",encoding="utf-8")
            snap=readiness(root/"sys/class/tty",
                which=lambda name: "/usr/bin/qFlipper" if name=="qFlipper" else None)
            self.assertTrue(snap["qflipper_installed"])
            self.assertEqual(len(snap["usb_serial_ports"]),1)
            row=snap["usb_serial_ports"][0]
            self.assertEqual(row["port"],"/dev/ttyACM0")
            self.assertFalse(row["device_identity_confirmed"])
            self.assertFalse(snap["verified_flipper_link"])

    def test_does_not_launch_or_flash_devices(self):
        source=Path(__file__).with_name("pi_readiness.py").read_text(encoding="utf-8")
        self.assertNotIn("subprocess.",source)
        self.assertNotIn("serial.Serial(",source)
        self.assertNotIn("os.system(",source)
        self.assertNotIn("flash(",source)


if __name__ == "__main__":
    unittest.main()
