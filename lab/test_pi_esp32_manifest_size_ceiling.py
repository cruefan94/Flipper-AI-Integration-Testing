"""Public-safe synthetic size ceiling regressions. No hardware, firmware or network I/O."""
import hashlib
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pi_esp32_flash_manifest_gate import inspect_manifest, MAX_IMAGE_BYTES
from pi_esp32_image_bytes_gate import inspect_image_bytes

def sample(size):
    payload = b"public-safe-synthetic"
    return {
        "board": "esp32-wroom-32",
        "board_identity_verified": True,
        "transport": "usb_serial",
        "image_sha256": hashlib.sha256(payload).hexdigest(),
        "image_bytes": size,
        "owner_approved": True,
    }

class ManifestSizeCeilingTests(unittest.TestCase):
    def test_oversize_metadata_rejected_without_allocating_image(self):
        result = inspect_manifest(sample(MAX_IMAGE_BYTES + 1))
        self.assertFalse(result["valid_metadata"])
        self.assertIn("image_size", result["errors"])
        self.assertFalse(result["flash_authorized"])

    def test_boolean_image_size_rejected(self):
        self.assertIn("image_size", inspect_manifest(sample(True))["errors"])

    def test_zero_image_size_rejected(self):
        self.assertIn("image_size", inspect_manifest(sample(0))["errors"])

    def test_upper_boundary_metadata_only_not_authorization(self):
        result = inspect_manifest(sample(MAX_IMAGE_BYTES))
        self.assertTrue(result["valid_metadata"])
        self.assertFalse(result["flash_authorized"])

    def test_byte_integrity_gate_rejects_oversize_declaration(self):
        result = inspect_image_bytes(sample(MAX_IMAGE_BYTES + 1), b"public-safe-synthetic")
        self.assertFalse(result["image_integrity_verified"])
        self.assertFalse(result["flash_authorized"])
        self.assertIn("image_size", result["errors"])

if __name__ == "__main__":
    unittest.main()
