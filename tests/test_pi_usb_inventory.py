"""Synthetic sysfs tests; never touch USB devices."""
import tempfile
import unittest
from pathlib import Path
from raspberry_pi.pi_usb_inventory import inventory


class InventoryTests(unittest.TestCase):
    def test_empty_or_missing_sysfs(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(inventory(Path(d) / "absent"), [])

    def test_usb_identification_and_no_serial_leak(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bus = root / "bus"
            bus.mkdir()
            for name, value in {"idVendor": "0483", "idProduct": "5740",
                                "manufacturer": "Example", "product": "USB Device",
                                "serial": "PRIVATE-SERIAL"}.items():
                (bus / name).write_text(value)
            interface = bus / "interface"
            interface.mkdir()
            tty = root / "tty"
            tty.mkdir()
            port = tty / "ttyACM0"
            port.mkdir()
            (port / "device").symlink_to(interface, target_is_directory=True)
            (tty / "ttyS0").mkdir()
            result = inventory(tty)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["port"], "/dev/ttyACM0")
            self.assertEqual(result[0]["vid"], "0483")
            self.assertNotIn("PRIVATE-SERIAL", str(result))

    def test_unidentified_port_is_not_assumed_esp32(self):
        with tempfile.TemporaryDirectory() as d:
            tty = Path(d)
            port = tty / "ttyUSB2"
            port.mkdir()
            (port / "device").symlink_to(tty, target_is_directory=True)
            result = inventory(tty)
            self.assertEqual(result[0]["vid"], None)
            self.assertEqual(result[0]["product"], None)


if __name__ == "__main__":
    unittest.main()
