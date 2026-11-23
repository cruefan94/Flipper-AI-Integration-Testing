import unittest
from pi_lab.monitor_text_view import format_snapshot

class MonitorTextViewTests(unittest.TestCase):
    def test_missing_all_sources_stale(self):
        lines = format_snapshot({}).splitlines()
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], "Raspberry Pi: STALE")
        self.assertEqual(lines[1], "Pironman OLED: STALE")

    def test_fresh_observation(self):
        self.assertEqual(format_snapshot({"pi": ("observed", 10)}).splitlines()[0],
                         "Raspberry Pi: OBSERVED")

    def test_stale_observation_not_displayed_as_live(self):
        self.assertEqual(format_snapshot({"pi": ("observed", 11)}).splitlines()[0],
                         "Raspberry Pi: STALE")

    def test_disconnected_remains_disconnected_when_fresh(self):
        self.assertEqual(format_snapshot({"flipper": ("disconnected", 0)}).splitlines()[2],
                         "Flipper Zero: DISCONNECTED")

    def test_reject_extra_private_fields(self):
        with self.assertRaises(ValueError):
            format_snapshot({"password": ("observed", 0)})

    def test_reject_invalid_age(self):
        with self.assertRaises(ValueError):
            format_snapshot({"esp32": ("observed", True)})

if __name__ == "__main__":
    unittest.main()
