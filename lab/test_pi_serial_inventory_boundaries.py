"""Public-safe negative fixtures for Pi serial inventory; no device I/O."""
import unittest
from pi_serial_inventory import inspect_inventory

class InventoryBoundaryTests(unittest.TestCase):
    def inspect(self, ports, devices=None):
        return inspect_inventory({"ports": ports, "usb_devices": [] if devices is None else devices})

    def test_null_inventory(self):
        self.assertFalse(inspect_inventory(None)["ready"])

    def test_extra_schema_field(self):
        self.assertIn("invalid inventory schema", inspect_inventory({"ports": [], "usb_devices": [], "command": "flash"})["errors"])

    def test_oversized_port_list(self):
        self.assertIn("invalid inventory lists", self.inspect([{}] * 65)["errors"])

    def test_oversized_usb_list(self):
        self.assertIn("invalid inventory lists", self.inspect([], [{}] * 65)["errors"])

    def test_boolean_vid_rejected(self):
        self.assertIn("invalid port identity", self.inspect([{"path": "/dev/ttyUSB0", "vid": True, "pid": "0001"}])["errors"])

    def test_unicode_confusable_port_rejected(self):
        self.assertIn("invalid port identity", self.inspect([{"path": "/dev/ttyUSB０", "vid": "10c4", "pid": "ea60"}])["errors"])

    def test_relative_path_rejected(self):
        self.assertIn("invalid port identity", self.inspect([{"path": "../ttyUSB0", "vid": "10c4", "pid": "ea60"}])["errors"])

    def test_candidate_does_not_imply_flash_permission(self):
        r = self.inspect([{"path": "/dev/ttyACM0", "vid": "303a", "pid": "1001"}])
        self.assertEqual(r["errors"], [])
        self.assertFalse(r["ready"])
        self.assertIn("manual", r["candidates"][0]["status"])

if __name__ == "__main__":
    unittest.main()
