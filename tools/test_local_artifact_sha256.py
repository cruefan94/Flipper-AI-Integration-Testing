"""Synthetic, offline tests; no private firmware or Android APK."""
import hashlib
import pathlib
import tempfile
import unittest
from check_local_artifact_sha256 import verify, main

class TestArtifactSHA(unittest.TestCase):
    def test_match_and_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "synthetic.bin"
            p.write_bytes(b"synthetic-only")
            expected = hashlib.sha256(b"synthetic-only").hexdigest()
            self.assertTrue(verify(p, expected.upper()))
            self.assertEqual(main([str(p), expected]), 0)
            p.write_bytes(b"changed")
            self.assertFalse(verify(p, expected))
            self.assertEqual(main([str(p), expected]), 1)

    def test_rejects_invalid_digest_and_missing_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "artifact"
            p.write_bytes(b"x")
            with self.assertRaises(ValueError):
                verify(p, "not-a-digest")
            with self.assertRaises(ValueError):
                verify(pathlib.Path(td) / "missing", "0" * 64)

    def test_rejects_directory_and_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "artifact"
            p.write_bytes(b"x")
            with self.assertRaises(ValueError):
                verify(pathlib.Path(td), "0" * 64)
            link = pathlib.Path(td) / "link"
            link.symlink_to(p)
            with self.assertRaises(ValueError):
                verify(link, "0" * 64)

if __name__ == "__main__":
    unittest.main()
