"""Synthetic-only integrity gate regression tests; no real firmware or device I/O."""
import hashlib
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pi_esp32_image_bytes_gate import inspect_image_bytes

PAYLOAD = b"synthetic-public-fixture-not-firmware"

def manifest(payload=PAYLOAD):
    return {"board": "esp32-wroom-32", "board_identity_verified": True,
            "transport": "usb_serial", "image_sha256": hashlib.sha256(payload).hexdigest(),
            "image_bytes": len(payload), "owner_approved": True}

class ImageIntegrityTests(unittest.TestCase):
    def test_matching_bytes_never_authorize_flash(self):
        result = inspect_image_bytes(manifest(), PAYLOAD)
        self.assertTrue(result["image_integrity_verified"])
        self.assertFalse(result["flash_authorized"])

    def test_changed_byte_rejected(self):
        result = inspect_image_bytes(manifest(), PAYLOAD[:-1] + b"X")
        self.assertIn("image_hash_mismatch", result["errors"])

    def test_truncated_payload_rejected(self):
        result = inspect_image_bytes(manifest(), PAYLOAD[:-1])
        self.assertIn("image_size_mismatch", result["errors"])

    def test_non_bytes_rejected(self):
        self.assertIn("image_type", inspect_image_bytes(manifest(), "text")["errors"])

    def test_empty_bytes_rejected(self):
        self.assertIn("image_empty", inspect_image_bytes(manifest(), b"")["errors"])

    def test_oversize_rejected(self):
        result = inspect_image_bytes(manifest(), b"x" * (16 * 1024 * 1024 + 1))
        self.assertIn("image_limit", result["errors"])

    def test_missing_owner_approval_stays_blocked(self):
        data = manifest()
        data["owner_approved"] = False
        result = inspect_image_bytes(data, PAYLOAD)
        self.assertFalse(result["image_integrity_verified"])
        self.assertFalse(result["flash_authorized"])

    def test_s2_separate_board_still_not_flash_authorized(self):
        data = manifest()
        data["board"] = "esp32-s2-devboard"
        result = inspect_image_bytes(data, PAYLOAD)
        self.assertTrue(result["image_integrity_verified"])
        self.assertFalse(result["flash_authorized"])

    def test_schema_error_no_private_values_echoed(self):
        result = inspect_image_bytes({"secret": "never-echo"}, PAYLOAD)
        self.assertEqual(result["errors"], ["schema"])
        self.assertNotIn("never-echo", str(result))

if __name__ == "__main__":
    unittest.main()
