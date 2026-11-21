"""Synthetic offline tests; no serial ports, radio or hardware."""
import unittest
from lab.esp32_power_domain_preflight import review


def link(a="arduino_uno", b="esp32_wroom", signal="uart", shift=True, ground=True):
    return {"source": a, "target": b, "signal": signal,
            "level_shifter_verified": shift, "common_ground_verified": ground}


class PreflightTests(unittest.TestCase):
    def test_verified_5v_to_3v3(self): self.assertEqual(review({"connections": [link()]}), [])
    def test_unshifted_5v_rejected(self): self.assertTrue(review({"connections": [link(shift=False)]}))
    def test_no_ground_rejected(self): self.assertTrue(review({"connections": [link(ground=False)]}))
    def test_s2_no_shift_required_from_flipper(self): self.assertEqual(review({"connections": [link("flipper_gpio", "esp32_s2", shift=False)]}), [])
    def test_reverse_direction(self): self.assertEqual(review({"connections": [link("esp32_wroom", "arduino_uno", shift=False)]}), [])
    def test_power_rail_rejected(self): self.assertTrue(review({"connections": [link(signal="power")]}))
    def test_unknown_board_rejected(self): self.assertTrue(review({"connections": [link(b="mystery")]}))
    def test_missing_links_rejected(self): self.assertTrue(review({"connections": []}))
    def test_extra_fields_rejected(self):
        v = link(); v["pin"] = "GPIO0"
        self.assertTrue(review({"connections": [v]}))
    def test_missing_flags_rejected(self):
        v = link(); del v["common_ground_verified"]
        self.assertTrue(review({"connections": [v]}))


if __name__ == "__main__":
    unittest.main()
