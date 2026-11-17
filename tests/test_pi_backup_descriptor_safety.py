"""Synthetic descriptor safety regressions; no real backups or devices."""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from raspberry_pi.pi_backup_manifest_verify import verify_manifest


class DescriptorSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.payload = b"synthetic-backup"
        (self.root / "good.bin").write_bytes(self.payload)
        self.entry = {"path": "good.bin", "size": len(self.payload),
                      "sha256": hashlib.sha256(self.payload).hexdigest()}

    def test_regular_file_still_verifies(self):
        self.assertTrue(verify_manifest(self.root, {"files": [self.entry]})["ok"])

    def test_symlink_swapped_after_path_check_is_not_followed(self):
        link = self.root / "swapped.bin"
        link.symlink_to(self.root / "good.bin")
        # Simulate a path being replaced after the original lstat validation.
        with patch("raspberry_pi.pi_backup_manifest_verify._safe_path", return_value=link):
            result = verify_manifest(self.root, {"files": [self.entry]})
        self.assertFalse(result["ok"])
        self.assertEqual(result["results"][0]["status"], "not_regular_file")

    def test_symlink_substituted_at_open_is_not_followed(self):
        # The initial lstat sees a regular file; replace it at the open boundary.
        # This verifies O_NOFOLLOW, rather than only pre-open path validation.
        target = self.root / "other.bin"
        target.write_bytes(b"other synthetic data")
        original_open = os.open
        swapped = False

        def swap_then_open(path, flags, *args, **kwargs):
            nonlocal swapped
            # Confined opens use a relative filename plus the pinned dir_fd.
            if not swapped and path == "good.bin" and kwargs.get("dir_fd") is not None:
                swapped = True
                (self.root / "good.bin").unlink()
                (self.root / "good.bin").symlink_to(target)
            return original_open(path, flags, *args, **kwargs)

        with patch("raspberry_pi.pi_backup_manifest_verify.os.open", side_effect=swap_then_open):
            result = verify_manifest(self.root, {"files": [self.entry]})
        self.assertTrue(swapped)
        self.assertFalse(result["ok"])
        self.assertEqual(result["results"][0]["status"], "read_error")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO required")
    def test_fifo_swapped_after_path_check_is_not_read(self):
        fifo = self.root / "swapped.fifo"
        os.mkfifo(fifo)
        with patch("raspberry_pi.pi_backup_manifest_verify._safe_path", return_value=fifo):
            result = verify_manifest(self.root, {"files": [self.entry]})
        self.assertFalse(result["ok"])
        self.assertEqual(result["results"][0]["status"], "not_regular_file")


if __name__ == "__main__":
    unittest.main()
