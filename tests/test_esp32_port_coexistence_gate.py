"""No hardware access: synthetic offline preflight tests."""
import unittest
from esp32_port_coexistence_gate import inspect_port_plan

def board(label="WROOM", chip="esp32-wroom-32", port="/dev/ttyUSB0", verified=True):
    return dict(label=label, claimed_chip=chip, port=port, identity_verified=verified)

class CoexistenceTests(unittest.TestCase):
    def test_distinct_boards(self):
        result = inspect_port_plan([board(), board("S2", "esp32-s2", "/dev/ttyACM0")])
        self.assertTrue(result["valid"])
        self.assertFalse(result["flash_authorized"])
    def test_same_port(self):
        self.assertIn("device_1_duplicate_port", inspect_port_plan([board(), board("S2", "esp32-s2")])["errors"])
    def test_case_insensitive_windows_port(self):
        self.assertIn("device_1_duplicate_port", inspect_port_plan([board(port="COM4"), board("S2", "esp32-s2", "com4")])["errors"])
    def test_unverified_identity(self):
        self.assertIn("device_0_identity_unverified", inspect_port_plan([board(verified=False)])["errors"])
    def test_boolean_only(self):
        self.assertFalse(inspect_port_plan([board(verified=1)])["valid"])
    def test_unknown_chip(self):
        self.assertIn("device_0_chip", inspect_port_plan([board(chip="esp32-s3")])["errors"])
    def test_duplicate_label(self):
        self.assertIn("device_1_duplicate_label", inspect_port_plan([board(), board("wroom", "esp32-s2", "COM4")])["errors"])
    def test_injection_port(self):
        self.assertFalse(inspect_port_plan([board(port="/dev/ttyUSB0;rm -rf /")])["valid"])
    def test_bad_record(self):
        self.assertFalse(inspect_port_plan([None])["valid"])
    def test_empty_list(self):
        self.assertFalse(inspect_port_plan([])["valid"])
    def test_extra_field(self):
        self.assertFalse(inspect_port_plan([dict(board(), owner_approved=True)])["valid"])
    def test_no_authorization_on_invalid(self):
        self.assertFalse(inspect_port_plan([board(verified=False)])["flash_authorized"])

    def test_blank_label(self):
        self.assertIn("device_0_label", inspect_port_plan([board(label="   ")])["errors"])
    def test_linux_port_case_sensitive(self):
        self.assertIn("device_0_port", inspect_port_plan([board(port="/dev/ttyusb0")])["errors"])
    def test_windows_port_lowercase_allowed(self):
        self.assertTrue(inspect_port_plan([board(port="com12")])["valid"])
    def test_fail_closed_all_cases(self):
        for port in ("/dev/ttyusb0", "COM0", "COM4;echo", "/dev/ttyUSB0\\n"):
            with self.subTest(port=port):
                result = inspect_port_plan([board(port=port)])
                self.assertFalse(result["valid"])
                self.assertFalse(result["flash_authorized"])

    def test_linux_usb_leading_zero_rejected(self):
        self.assertIn("device_0_port", inspect_port_plan([board(port="/dev/ttyUSB00")])["errors"])
    def test_linux_acm_leading_zero_rejected(self):
        self.assertIn("device_0_port", inspect_port_plan([board(port="/dev/ttyACM01")])["errors"])
    def test_standard_linux_ports_allowed(self):
        self.assertTrue(inspect_port_plan([board(), board("S2", "esp32-s2", "/dev/ttyACM1")])["valid"])
    def test_oversized_port_rejected(self):
        self.assertFalse(inspect_port_plan([board(port="/dev/ttyUSB" + "9" * 100)])["valid"])
    def test_no_flash_authorization_after_valid_canonical_port(self):
        self.assertFalse(inspect_port_plan([board()])["flash_authorized"])

    def test_mixed_host_ports_rejected(self):
        result = inspect_port_plan([board(), board("S2", "esp32-s2", "COM4")])
        self.assertIn("mixed_host_port_families", result["errors"])
        self.assertFalse(result["flash_authorized"])

    def test_same_host_linux_allowed(self):
        self.assertTrue(inspect_port_plan([board(), board("S2", "esp32-s2", "/dev/ttyACM1")])["valid"])

    def test_same_host_windows_allowed(self):
        self.assertTrue(inspect_port_plan([board(port="COM3"), board("S2", "esp32-s2", "COM4")])["valid"])

if __name__ == "__main__":
    unittest.main()
