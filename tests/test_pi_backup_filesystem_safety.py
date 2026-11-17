"""Synthetic regression tests for backup verifier filesystem edge cases.

Never touches physical Pi, Flipper, serial ports or real backups.
"""
import hashlib
import tempfile
import unittest
from pathlib import Path

from raspberry_pi.pi_backup_manifest_verify import verify_manifest


class BackupFilesystemSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.backup = self.root / "backup"
        self.backup.mkdir()

    @staticmethod
    def entry(path, data):
        return {"path": path, "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest()}

    def test_empty_regular_file_is_valid_when_listed(self):
        (self.backup / "empty.bin").write_bytes(b"")
        result = verify_manifest(self.backup, {"files": [self.entry("empty.bin", b"")]})
        self.assertTrue(result["ok"])
        self.assertEqual(result["results"], [{"status": "ok"}])

    def test_directory_cannot_masquerade_as_file(self):
        (self.backup / "dir").mkdir()
        result = verify_manifest(self.backup, {"files": [self.entry("dir", b"")]})
        self.assertFalse(result["ok"])
        self.assertEqual(result["results"][0]["status"], "not_regular_file")

    def test_root_symlink_rejected(self):
        link = self.root / "backup_link"
        link.symlink_to(self.backup, target_is_directory=True)
        result = verify_manifest(link, {"files": [self.entry("x", b"")]})
        self.assertFalse(result["ok"])
        self.assertEqual(result["results"][0]["status"], "invalid_root")

    def test_nested_regular_file_is_verified(self):
        folder = self.backup / "nested"
        folder.mkdir()
        (folder / "data.bin").write_bytes(b"test")
        result = verify_manifest(
            self.backup, {"files": [self.entry("nested/data.bin", b"test")]}
        )
        self.assertTrue(result["ok"])

    def test_failed_entry_does_not_expose_file_path(self):
        private_name = "synthetic-private-name.bin"
        result = verify_manifest(
            self.backup, {"files": [self.entry(private_name, b"missing")]}
        )
        self.assertFalse(result["ok"])
        self.assertNotIn(private_name, str(result))


if __name__ == "__main__":
    unittest.main()
