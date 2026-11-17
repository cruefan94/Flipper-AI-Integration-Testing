"""Synthetic root-directory swap tests for read-only backup verification.

No hardware, real backup, or privileged operations are accessed.
"""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from raspberry_pi.pi_backup_manifest_verify import verify_manifest


@unittest.skipUnless(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"),
                     "POSIX no-follow directory opening required")
class RootRaceTests(unittest.TestCase):
    def test_root_symlink_substitution_before_open_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "backup"
            root.mkdir()
            payload = b"synthetic root swap payload"
            (root / "sample.bin").write_bytes(payload)
            outside = parent / "outside"
            outside.mkdir()
            (outside / "sample.bin").write_bytes(payload)
            manifest = {"files": [{"path": "sample.bin", "size": len(payload),
                                   "sha256": hashlib.sha256(payload).hexdigest()}]}
            real_open = os.open
            swapped = False

            def swap_root(path, flags, *args, **kwargs):
                nonlocal swapped
                if not swapped and os.fspath(path) == os.fspath(root):
                    swapped = True
                    root.rename(parent / "original")
                    root.symlink_to(outside, target_is_directory=True)
                return real_open(path, flags, *args, **kwargs)

            with patch("raspberry_pi.pi_backup_manifest_verify.os.open",
                       side_effect=swap_root):
                result = verify_manifest(root, manifest)
            self.assertTrue(swapped)
            self.assertFalse(result["ok"])
            self.assertEqual(result["results"][0]["status"], "read_error")
            self.assertNotIn(str(root), str(result))
            self.assertNotIn("sample.bin", str(result))

    def test_normal_root_remains_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = b"synthetic backup"
            target = root / "sample.bin"
            target.write_bytes(payload)
            manifest = {"files": [{"path": "sample.bin", "size": len(payload),
                                   "sha256": hashlib.sha256(payload).hexdigest()}]}
            result = verify_manifest(root, manifest)
            self.assertTrue(result["ok"])
            self.assertEqual(target.read_bytes(), payload)
            self.assertFalse(result["identity_verified"])


if __name__ == "__main__":
    unittest.main()
