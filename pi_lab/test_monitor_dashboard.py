import unittest

from pi_lab.monitor_dashboard import render_rows


class DashboardRowsTests(unittest.TestCase):
    def test_four_fixed_rows_with_no_observations(self):
        rows = render_rows({})
        self.assertEqual([row.source for row in rows], ["pi", "oled", "flipper", "esp32"])
        self.assertTrue(all(row.state == "UNKNOWN" and row.freshness == "STALE" for row in rows))

    def test_exact_ten_seconds_fresh(self):
        self.assertEqual(render_rows({"pi": ("observed", 10)})[0].freshness, "FRESH")

    def test_eleven_seconds_stale(self):
        self.assertEqual(render_rows({"oled": ("observed", 11)})[1].freshness, "STALE")

    def test_disconnected_never_becomes_observed(self):
        self.assertEqual(render_rows({"flipper": ("disconnected", 0)})[2].state, "DISCONNECTED")

    def test_all_source_labels_fixed(self):
        self.assertEqual([row.label for row in render_rows({})],
                         ["Raspberry Pi", "Pironman OLED", "Flipper Zero", "ESP32"])

    def test_reject_unexpected_secret_field(self):
        with self.assertRaises(ValueError):
            render_rows({"api_key": ("observed", 0)})

    def test_reject_arbitrary_state_text(self):
        with self.assertRaises(ValueError):
            render_rows({"pi": ("token=private", 0)})

    def test_reject_boolean_age(self):
        with self.assertRaises(ValueError):
            render_rows({"pi": ("observed", True)})


if __name__ == "__main__":
    unittest.main()
