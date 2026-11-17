"""Read-only integration readiness without physical hardware."""
import tempfile
import unittest
from pathlib import Path

from raspberry_pi.pi_project_readiness import readiness


class ProjectReadinessTests(unittest.TestCase):
    def test_absent_devices_are_not_claimed_verified(self):
        with tempfile.TemporaryDirectory() as root:
            result = readiness(Path(root) / "no-tty", Path(root), lambda name: None)
            self.assertTrue(result["read_only"])
            self.assertFalse(result["qflipper_installed"])
            self.assertEqual(result["serial_ports"], [])
            self.assertEqual(result["serial_port_count"], 0)
            self.assertFalse(result["flipper_detected_by_ai_protocol"])
            self.assertFalse(result["esp32_identity_verified"])
            self.assertFalse(result["arduino_identity_verified"])

    def test_qflipper_presence_does_not_imply_esp32_or_ai(self):
        with tempfile.TemporaryDirectory() as root:
            result = readiness(Path(root), Path(root),
                               lambda name: "/usr/bin/qFlipper" if name == "qFlipper" else None)
            self.assertTrue(result["qflipper_installed"])
            self.assertFalse(result["flipper_detected_by_ai_protocol"])
            self.assertFalse(result["esp32_identity_verified"])
            self.assertFalse(result["arduino_identity_verified"])

    def test_report_warns_against_unsafe_arduino_connections(self):
        with tempfile.TemporaryDirectory() as root:
            output = readiness(Path(root), Path(root), lambda name: None)
            self.assertIn("5V Arduino GPIO", " ".join(output["next_steps"]))


if __name__ == "__main__":
    unittest.main()
