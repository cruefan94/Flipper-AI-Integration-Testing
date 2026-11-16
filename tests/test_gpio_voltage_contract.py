import unittest
from lab_contracts.gpio_voltage import Pin, check_signal, UNO_DIGITAL_OUT, ESP32_GPIO_IN, FLIPPER_GPIO_IN

class VoltageContractTests(unittest.TestCase):
    def test_uno_to_esp32_rejected(self):
        self.assertEqual(check_signal(UNO_DIGITAL_OUT, ESP32_GPIO_IN)["reason"], "overvoltage")

    def test_uno_to_flipper_rejected(self):
        self.assertFalse(check_signal(UNO_DIGITAL_OUT, FLIPPER_GPIO_IN)["safe"])

    def test_shifter_flag_does_not_bypass(self):
        self.assertFalse(check_signal(UNO_DIGITAL_OUT, ESP32_GPIO_IN, level_shifter=True)["safe"])

    def test_esp32_to_uno_voltage_only(self):
        self.assertTrue(check_signal(Pin("esp32", "GPIO17", "out", 3.3, 3.3), Pin("uno", "D3", "in", 0, 5))["safe"])

    def test_unknown_board_rejected(self):
        self.assertFalse(check_signal(Pin("other", "X", "out", 3.3, 3.3), ESP32_GPIO_IN)["safe"])

    def test_wrong_direction_rejected(self):
        self.assertFalse(check_signal(ESP32_GPIO_IN, UNO_DIGITAL_OUT)["safe"])

if __name__ == "__main__":
    unittest.main()
