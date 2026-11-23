"""Public-safe synthetic fixtures only; no firmware, device or network access."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from pi_esp32_stream_integrity_gate import inspect_local_image

DATA = b"synthetic-public-esp32-test-image"

def manifest(data=DATA):
    return {"board": "esp32-wroom-32", "board_identity_verified": True,
            "transport": "usb_serial", "image_sha256": hashlib.sha256(data).hexdigest(),
            "image_bytes": len(data), "owner_approved": True}

class StreamingIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "synthetic.bin"
        self.path.write_bytes(DATA)

    def test_valid_synthetic_file(self):
        self.assertTrue(inspect_local_image(manifest(), self.path)["image_integrity_verified"])

    def test_never_authorizes_flash(self):
        self.assertFalse(inspect_local_image(manifest(), self.path)["flash_authorized"])

    def test_hash_mismatch(self):
        self.path.write_bytes(b"x" * len(DATA))
        self.assertIn("image_hash_mismatch", inspect_local_image(manifest(), self.path)["errors"])

    def test_size_mismatch(self):
        self.path.write_bytes(DATA + b"x")
        self.assertIn("image_size_mismatch", inspect_local_image(manifest(), self.path)["errors"])

    def test_missing_file(self):
        self.path.unlink()
        self.assertIn("image_open", inspect_local_image(manifest(), self.path)["errors"])

    def test_symlink_refused(self):
        link = Path(self.temp.name) / "alias.bin"
        link.symlink_to(self.path)
        self.assertFalse(inspect_local_image(manifest(), link)["image_integrity_verified"])

    def test_directory_refused(self):
        self.assertIn("image_not_regular", inspect_local_image(manifest(), Path(self.temp.name))["errors"])

    def test_invalid_manifest_prevents_file_open(self):
        bad = manifest()
        bad["owner_approved"] = False
        self.assertIn("owner_approval", inspect_local_image(bad, self.path)["errors"])

    def test_empty_file(self):
        self.path.write_bytes(b"")
        self.assertIn("image_size_limit", inspect_local_image(manifest(), self.path)["errors"])

if __name__ == "__main__":
    unittest.main()
