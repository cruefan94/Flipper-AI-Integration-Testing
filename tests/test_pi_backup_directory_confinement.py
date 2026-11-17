"""Read-only directory descriptor confinement regressions (synthetic only)."""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from raspberry_pi.pi_backup_manifest_verify import verify_manifest


@unittest.skipUnless(hasattr(os, "O_DIRECTORY") and hasattr(os, "O_NOFOLLOW"),
                     "POSIX descriptor confinement required")
class DirectoryConfinementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "backup"
        self.root.mkdir()
        (self.root / "nested").mkdir()
        self.payload = b"synthetic nested backup"
        (self.root / "nested" / "file.bin").write_bytes(self.payload)
        self.manifest = {"files": [{"path": "nested/file.bin",
                                    "size": len(self.payload),
                                    "sha256": hashlib.sha256(self.payload).hexdigest()}]}

    def test_nested_regular_file_passes(self):
        result = verify_manifest(self.root, self.manifest)
        self.assertTrue(result["ok"])

    def test_intermediate_directory_symlink_swap_fails_closed(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (outside / "file.bin").write_bytes(self.payload)
        real_open = os.open
        swapped = False

        def swap_at_open(path, flags, *args, **kwargs):
            nonlocal swapped
            if path == "nested" and "dir_fd" in kwargs and not swapped:
                swapped = True
                (self.root / "nested").rename(self.root / "moved")
                (self.root / "nested").symlink_to(outside, target_is_directory=True)
            return real_open(path, flags, *args, **kwargs)

        with patch("raspberry_pi.pi_backup_manifest_verify.os.open",
                   side_effect=swap_at_open):
            result = verify_manifest(self.root, self.manifest)
        self.assertTrue(swapped)
        self.assertFalse(result["ok"])
        self.assertEqual(result["results"][0]["status"], "read_error")

    def test_no_private_paths_in_failure_result(self):
        (self.root / "nested" / "file.bin").unlink()
        result = verify_manifest(self.root, self.manifest)
        self.assertFalse(result["ok"])
        self.assertNotIn(str(self.root), str(result))
        self.assertNotIn("file.bin", str(result))


if __name__ == "__main__":
    unittest.main()
