"""Hardware-free regression tests for Pi USB inventory comparison."""
import unittest

from raspberry_pi.pi_usb_snapshot_diff import compare_snapshots


def device(port, vid="0483", pid="5740", product="Example"):
    return {"port": port, "vid": vid, "pid": pid,
            "manufacturer": "Example", "product": product}


class SnapshotDiffTests(unittest.TestCase):
    def test_attach_detach_sorted(self):
        before = [device("/dev/ttyACM1"), device("/dev/ttyUSB2")]
        after = [device("/dev/ttyACM0"), device("/dev/ttyUSB2")]
        result = compare_snapshots(before, after)
        self.assertEqual(result["connected"], ["/dev/ttyACM0"])
        self.assertEqual(result["disconnected"], ["/dev/ttyACM1"])
        self.assertEqual(result["metadata_changed"], [])
        self.assertFalse(result["identity_verified"])
        self.assertTrue(result["read_only"])

    def test_same_port_metadata_change_is_not_verified_identity(self):
        result = compare_snapshots(
            [device("/dev/ttyUSB0", product="Old")],
            [device("/dev/ttyUSB0", product="New")])
        self.assertEqual(result["metadata_changed"], ["/dev/ttyUSB0"])
        self.assertFalse(result["identity_verified"])

    def test_unchanged_and_invalid_entries(self):
        valid = device("/dev/ttyACM0")
        result = compare_snapshots([valid, {"port": "/dev/ttyS0"}],
                                   [valid, {"port": "/tmp/ttyUSB0"}])
        self.assertEqual(result["connected"], [])
        self.assertEqual(result["disconnected"], [])
        self.assertEqual(result["metadata_changed"], [])

    def test_input_not_mutated_or_serial_exposed(self):
        before = [{**device("/dev/ttyUSB1"), "serial": "SECRET-SERIAL"}]
        after = [{**device("/dev/ttyUSB1"), "serial": "OTHER-SECRET"}]
        saved = [dict(before[0])]
        result = compare_snapshots(before, after)
        self.assertEqual(before, saved)
        self.assertNotIn("SECRET", str(result))
        self.assertEqual(result["metadata_changed"], [])


if __name__ == "__main__":
    unittest.main()
