import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from esp32s2_bundle_preflight import verify


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.payload = b"fixture only - not firmware"
        (self.root / "image.bin").write_bytes(self.payload)
        self.manifest = self.root / "manifest.json"
        self.data = {"chip": "esp32s2", "images": [{"file": "image.bin", "offset": "0x10000", "sha256": hashlib.sha256(self.payload).hexdigest()}]}
        self.write()

    def write(self):
        self.manifest.write_text(json.dumps(self.data))

    def test_valid(self):
        self.assertEqual(verify(self.manifest), 1)

    def test_wrong_chip(self):
        self.data["chip"] = "esp32"
        self.write()
        with self.assertRaises(ValueError): verify(self.manifest)

    def test_corrupt_hash(self):
        self.data["images"][0]["sha256"] = "0" * 64
        self.write()
        with self.assertRaises(ValueError): verify(self.manifest)

    def test_unsafe_path(self):
        self.data["images"][0]["file"] = "../image.bin"
        self.write()
        with self.assertRaises(ValueError): verify(self.manifest)

    def test_overlap(self):
        self.data["images"].append(dict(self.data["images"][0]))
        self.write()
        with self.assertRaises(ValueError): verify(self.manifest)

    def test_unaligned(self):
        self.data["images"][0]["offset"] = "0x10001"
        self.write()
        with self.assertRaises(ValueError): verify(self.manifest)


if __name__ == "__main__":
    unittest.main()
