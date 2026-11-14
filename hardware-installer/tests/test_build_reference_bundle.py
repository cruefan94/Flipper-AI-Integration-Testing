"""Reference .bin bundle: SHA integrity and explicit UNTESTED identity."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_esp32_reference_bundle import package
from verify_bundle import BundleError, inspect

class ReferenceBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.build=self.root/"esp32dev"
        self.build.mkdir()
        for name,contents in (
            ("bootloader.bin",b"\xE9"+b"BOOT"*18),
            ("partitions.bin",b"\xAA\x50"+b"PART"*18),
            ("firmware.bin",b"\xE9"+b"APP"*170)
        ):
            (self.build/name).write_bytes(contents)
        self.dest=self.root/"bundle"

    def test_generated_bundle_is_valid_but_hardware_unverified(self):
        path=package(self.build,self.dest,"0.1.0-dev","test-commit")
        doc=json.loads(path.read_text())
        self.assertEqual(doc["board_id"],"esp32_wroom32_devkit")
        self.assertEqual(doc["chip"],"esp32")
        self.assertEqual(doc["flash_size_bytes"],4*1024*1024)
        self.assertTrue(doc["hardware_confirmation_required"])
        self.assertEqual(doc["source_revision"],"test-commit")
        self.assertEqual(
            [x["offset"] for x in doc["images"]],
            ["0x1000","0x8000","0x10000"])
        board,_,imgs=inspect(path,"esp32_wroom32_devkit")
        self.assertEqual(board.chip,"esp32")
        self.assertEqual(len(imgs),3)
        for x in doc["images"]:
            self.assertEqual(x["sha256"],
                hashlib.sha256((self.dest/x["file"]).read_bytes()).hexdigest())
        notice=(self.dest/"READ_ME_BEFORE_FLASHING.txt").read_text()
        self.assertIn("NOT VERIFIED",notice)
        self.assertIn("4 MiB",notice)
        self.assertIn("DOES NOT FLASH",notice)

    def test_does_not_overwrite_an_existing_bundle(self):
        package(self.build,self.dest,"0.1.0-dev")
        with self.assertRaisesRegex(BundleError,"overwrite"):
            package(self.build,self.dest,"0.1.0-dev")

    def test_corrupt_image_refused_before_any_output(self):
        (self.build/"firmware.bin").write_bytes(b"not-an-esp32-image")
        with self.assertRaisesRegex(BundleError,"binary magic"):
            package(self.build,self.dest,"0.1.0-dev")
        self.assertFalse(self.dest.exists())

    def test_incomplete_build_refused_before_any_output(self):
        (self.build/"partitions.bin").unlink()
        with self.assertRaisesRegex(BundleError,"missing"):
            package(self.build,self.dest,"0.1.0-dev")
        self.assertFalse(self.dest.exists())

    def test_unknown_version_and_revision_labels_rejected(self):
        with self.assertRaisesRegex(BundleError,"version"):
            package(self.build,self.dest,"../unsafe")
        with self.assertRaisesRegex(BundleError,"revision"):
            package(self.build,self.dest,"0.1.0-dev", "../unsafe")
        self.assertFalse(self.dest.exists())

if __name__=="__main__": unittest.main()
