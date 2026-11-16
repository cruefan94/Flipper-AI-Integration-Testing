import unittest
from esp32_boot_policy import Observation, review

def obs(**overrides):
    values = dict(chip="esp32", gpio0_at_reset="LOW",
                  reset_was_asserted=True, reset_was_released=True,
                  uart_port_identified=True)
    values.update(overrides)
    return Observation(**values)

class BootPolicyTests(unittest.TestCase):
    def test_possible_is_not_success(self):
        self.assertEqual(review(obs())["status"], "POSSIBLE")
    def test_s2_supported(self):
        self.assertEqual(review(obs(chip="esp32s2"))["status"], "POSSIBLE")
    def test_unknown_family_blocked(self):
        self.assertEqual(review(obs(chip="esp32c3"))["status"], "BLOCKED")
    def test_missing_reset(self):
        self.assertEqual(review(obs(reset_was_released=False))["status"], "INCOMPLETE")
    def test_high_gpio0_not_confirmed(self):
        self.assertEqual(review(obs(gpio0_at_reset="HIGH"))["status"], "NOT_CONFIRMED")
    def test_unverified_port(self):
        self.assertEqual(review(obs(uart_port_identified=False))["status"], "INCOMPLETE")
    def test_invalid_state(self):
        self.assertEqual(review(obs(gpio0_at_reset="FLOAT"))["status"], "BLOCKED")
    def test_no_hardware_access(self):
        self.assertEqual(review(obs())["status"], "POSSIBLE")

if __name__ == "__main__":
    unittest.main()
