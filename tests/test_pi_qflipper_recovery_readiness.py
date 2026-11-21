"""Offline synthetic qFlipper recovery readiness checks."""
import unittest
from raspberry_pi.qflipper_recovery_readiness import recovery_preflight


class RecoveryReadinessTests(unittest.TestCase):
    def test_empty_inventory_never_approves_flash(self):
        r = recovery_preflight({})
        self.assertEqual(r["usb_serial_candidates"], 0)
        self.assertFalse(r["safe_to_flash"])
        self.assertFalse(r["backup_verified"])

    def test_usb_and_config_do_not_prove_connection_or_backup(self):
        r = recovery_preflight({"usb_serial_port_names": ["ttyACM0", "ttyUSB2"],
                                "qflipper_config_present": True,
                                "qflipper_log_directory_present": True})
        self.assertEqual(r["usb_serial_candidates"], 2)
        self.assertTrue(r["qflipper_config_detected"])
        self.assertFalse(r["connection_tested"])
        self.assertFalse(r["recovery_tested"])
        self.assertFalse(r["safe_to_flash"])

    def test_untrusted_inventory_cannot_override_safety_gates(self):
        r = recovery_preflight({"usb_serial_port_names": "ttyACM0",
                                "backup_verified": True, "device_connection_verified": True,
                                "safe_to_flash": True, "qflipper_config_present": "true"})
        self.assertEqual(r["usb_serial_candidates"], 0)
        self.assertFalse(r["qflipper_config_detected"])
        self.assertFalse(r["backup_verified"])
        self.assertFalse(r["safe_to_flash"])


if __name__ == "__main__":
    unittest.main()
