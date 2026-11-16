"""Hardware-free regression cases for Pi serial inventory reconciliation."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lab"))
from serial_identity_inventory import reconcile_serial_inventory


class SerialInventoryTests(unittest.TestCase):
    def test_aliases_are_one_unverified_device(self):
        result = reconcile_serial_inventory([
            {"path": "/dev/ttyUSB0", "target": "/dev/ttyUSB0"},
            {"path": "/dev/serial/by-id/usb-CP210x_A", "target": "/dev/ttyUSB0"},
            {"path": "/dev/ttyACM0", "target": "/dev/ttyACM0"},
        ])
        self.assertEqual(len(result["devices"]), 2)
        self.assertEqual(result["devices"][1]["aliases"],
                         ["/dev/serial/by-id/usb-CP210x_A", "/dev/ttyUSB0"])
        self.assertTrue(all(d["chip"] == "unverified" and not d["flash_authorized"]
                            for d in result["devices"]))

    def test_rejects_traversal_and_nonserial(self):
        result = reconcile_serial_inventory([
            {"path": "/dev/ttyUSB0/../../etc/passwd", "target": "/dev/ttyUSB0"},
            {"path": "/tmp/ttyUSB0", "target": "/dev/ttyUSB0"},
            {"path": "/dev/ttyUSB0", "target": "/dev/sda"},
            {"path": "/dev/ttyUSB0", "target": "/dev/serial/by-id/alias"},
            None,
        ])
        self.assertEqual(result["devices"], [])
        self.assertEqual(len(result["errors"]), 5)

    def test_deterministic_and_duplicate_safe(self):
        records = [{"path": "/dev/ttyACM2", "target": "/dev/ttyACM2"}] * 2
        result = reconcile_serial_inventory(records)
        self.assertEqual(result["devices"][0]["aliases"], ["/dev/ttyACM2"])
        self.assertEqual(result["errors"], [])


if __name__ == "__main__":
    unittest.main()
