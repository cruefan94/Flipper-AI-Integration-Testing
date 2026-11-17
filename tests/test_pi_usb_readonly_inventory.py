"""Synthetic USB inventory tests: no physical device access."""
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from raspberry_pi.pi_usb_readonly_inventory import inventory, main


class USBInventoryTests(unittest.TestCase):
    def test_candidates_deduplicated_and_not_identified(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("ttyACM0", "ttyUSB2", "ttyS0", "ttyACMbad"):
                (root / name).mkdir()
            found = inventory(root)
            self.assertEqual([item["port"] for item in found],
                             ["/dev/ttyACM0", "/dev/ttyUSB2"])
            self.assertTrue(all(item["identity"] == "unconfirmed" for item in found))

    def test_missing_root_is_safe(self):
        with TemporaryDirectory() as temp:
            self.assertEqual(inventory(Path(temp) / "missing"), [])

    def test_cli_json_from_fixture(self):
        with TemporaryDirectory() as temp:
            (Path(temp) / "ttyACM1").mkdir()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["--sys-tty-root", temp]), 0)
            data = json.loads(output.getvalue())
            self.assertFalse(data["hardware_verified"])
            self.assertEqual(data["interfaces"][0]["port"], "/dev/ttyACM1")


if __name__ == "__main__":
    unittest.main()
