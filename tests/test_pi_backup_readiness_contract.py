"""Synthetic end-to-end contract: existing backup verifier -> read-only summary.

Never opens a device, changes cooling, restores data, or exposes private paths.
"""
import hashlib
import tempfile
import unittest
from pathlib import Path

from raspberry_pi.pi_backup_manifest_verify import verify_manifest
from raspberry_pi.pi_backup_readiness import summarize_readiness


class BackupReadinessContractTests(unittest.TestCase):
    def test_verified_backup_is_review_only_and_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = b"synthetic flipper backup content"
            target = root / "test.bin"
            target.write_bytes(payload)
            manifest = {"files": [{"path": "test.bin", "size": len(payload),
                                    "sha256": hashlib.sha256(payload).hexdigest()}]}
            result = summarize_readiness(verify_manifest(root, manifest))
            self.assertTrue(result["ready_for_manual_review"])
            self.assertEqual((result["verified_files"], result["failed_files"]), (1, 0))
            self.assertFalse(result["identity_verified"])
            self.assertFalse(result["restore_authorized"])
            self.assertEqual(target.read_bytes(), payload)
            self.assertNotIn(str(root), str(result))
            self.assertNotIn("test.bin", str(result))

    def test_corrupted_backup_blocks_review_and_does_not_expose_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "test.bin").write_bytes(b"modified")
            manifest = {"files": [{"path": "test.bin", "size": 8,
                                    "sha256": hashlib.sha256(b"original").hexdigest()}]}
            result = summarize_readiness(verify_manifest(root, manifest))
            self.assertFalse(result["ready_for_manual_review"])
            self.assertEqual(result["failed_files"], 1)
            self.assertFalse(result["restore_authorized"])
            self.assertNotIn("test.bin", str(result))

    def test_empty_manifest_cannot_be_review_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            result = summarize_readiness(verify_manifest(Path(temp), {"files": []}))
            self.assertFalse(result["ready_for_manual_review"])
            self.assertFalse(result["restore_authorized"])


if __name__ == "__main__":
    unittest.main()
