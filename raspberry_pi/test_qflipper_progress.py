"""Synthetic regression tests; no device, qFlipper or firmware required."""
import tempfile
import unittest
from pathlib import Path
from qflipper_progress import parse_line, observe

class QFlipperProgressTests(unittest.TestCase):
    def test_explicit_percent(self):
        self.assertEqual(parse_line("Firmware update: 47%")["percent"], 47)
        self.assertEqual(parse_line("Flashing 100%")["percent"], 100)
    def test_unrelated_percent_is_not_flash_progress(self):
        self.assertIsNone(parse_line("CPU 80%"))
        self.assertIsNone(parse_line("Battery 7%"))
        self.assertIsNone(parse_line("Update package loaded"))
    def test_failure_does_not_claim_progress(self):
        value = parse_line("Firmware update failed at 7%")
        self.assertEqual(value["status"], "failed")
        self.assertIsNone(value["percent"])
    def test_completion_not_inferred_as_100(self):
        value = parse_line("Firmware update completed")
        self.assertEqual(value["status"], "reported_complete")
        self.assertIsNone(value["percent"])
    def test_file_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.log"
            original = "CPU 90%\nFirmware update 17%\nFirmware update failed\n"
            path.write_text(original)
            events = list(observe(path))
            self.assertEqual([x["status"] for x in events], ["reported_progress", "failed"])
            self.assertEqual(path.read_text(), original)

if __name__ == "__main__":
    unittest.main()
