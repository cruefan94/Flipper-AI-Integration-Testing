import unittest
from pi_lab.read_only_monitor import summarize_snapshot, SOURCES


class MonitorSnapshotTests(unittest.TestCase):
    def test_missing_sources_are_unknown_and_stale(self):
        result = summarize_snapshot({})
        self.assertEqual(tuple(item.source for item in result), SOURCES)
        self.assertTrue(all(item.state == "unknown" and item.stale for item in result))

    def test_exact_ten_seconds_fresh(self):
        result = summarize_snapshot({"pi": ("observed", 10)})
        self.assertFalse(result[0].stale)

    def test_eleven_seconds_stale(self):
        self.assertTrue(summarize_snapshot({"oled": ("observed", 11)})[1].stale)

    def test_disconnected_is_not_automatically_observed(self):
        result = summarize_snapshot({"flipper": ("disconnected", 0)})
        self.assertEqual(result[2].state, "disconnected")

    def test_all_four_sources(self):
        result = summarize_snapshot({source: ("unavailable", 0) for source in SOURCES})
        self.assertEqual(len(result), 4)
        self.assertTrue(all(not item.stale for item in result))

    def test_unknown_key_rejected(self):
        with self.assertRaises(ValueError):
            summarize_snapshot({"serial_number": ("observed", 0)})

    def test_freeform_secrets_rejected(self):
        with self.assertRaises(ValueError):
            summarize_snapshot({"pi": ("token=secret", 0)})

    def test_invalid_age_rejected(self):
        for age in (-1, 86401, True, 0.5, "10"):
            with self.subTest(age=age), self.assertRaises(ValueError):
                summarize_snapshot({"pi": ("observed", age)})

    def test_invalid_shape_rejected(self):
        for value in ([], {"pi": ["observed", 0]}, {"pi": ("observed",)}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                summarize_snapshot(value)


if __name__ == "__main__":
    unittest.main()
