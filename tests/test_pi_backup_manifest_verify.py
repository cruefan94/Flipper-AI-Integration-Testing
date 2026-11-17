"""Synthetic-only checks; no real Flipper or Pi data accessed."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from raspberry_pi.pi_backup_manifest_verify import verify_manifest


class BackupManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "backup").mkdir()
        self.backup = self.root / "backup"
        (self.backup / "test.bin").write_bytes(b"synthetic data")
        self.entry = {"path": "test.bin", "size": 14,
                      "sha256": hashlib.sha256(b"synthetic data").hexdigest()}

    def check(self, entries):
        return verify_manifest(self.backup, {"files": entries})

    def test_valid_backup_is_not_modified(self):
        before = (self.backup / "test.bin").read_bytes()
        result = self.check([self.entry])
        self.assertTrue(result["ok"])
        self.assertTrue(result["read_only"])
        self.assertFalse(result["identity_verified"])
        self.assertEqual((self.backup / "test.bin").read_bytes(), before)

    def test_mismatch_and_missing_file_fail_closed(self):
        self.assertEqual(self.check([{**self.entry, "size": 15}])["results"][0]["status"], "mismatch")
        self.assertEqual(self.check([{**self.entry, "path": "missing.bin"}])["results"][0]["status"], "unsafe_or_missing_path")

    def test_path_traversal_and_absolute_path_rejected(self):
        for name in ("../outside", "/etc/passwd", "folder/../../outside", "a\\b"):
            with self.subTest(name=name):
                self.assertFalse(self.check([{**self.entry, "path": name}])["ok"])

    def test_symlink_escape_rejected(self):
        (self.backup / "escape").symlink_to(self.root, target_is_directory=True)
        self.assertEqual(self.check([{**self.entry, "path": "escape/test.bin"}])["results"][0]["status"], "unsafe_or_missing_path")

    def test_duplicate_and_invalid_entries_rejected(self):
        self.assertFalse(self.check([self.entry, self.entry])["ok"])
        for entry in ({**self.entry, "size": True},
                      {**self.entry, "sha256": "not-a-digest"},
                      {"path": "test.bin"}):
            self.assertEqual(self.check([entry])["results"][0]["status"], "invalid_entry")

    def test_empty_manifest_is_not_a_verified_backup(self):
        result = self.check([])
        self.assertFalse(result["ok"])
        self.assertEqual(result["results"][0]["status"], "invalid_manifest")

    def test_nonempty_manifest_still_verifies(self):
        result = self.check([self.entry])
        self.assertTrue(result["ok"])

    def test_bad_manifest_and_missing_root(self):
        self.assertFalse(verify_manifest(self.backup, {"files": "wrong"})["ok"])
        self.assertFalse(verify_manifest(self.root / "missing", {"files": []})["ok"])


if __name__ == "__main__":
    unittest.main()
