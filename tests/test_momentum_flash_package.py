#!/usr/bin/env python3
"""Public-safe synthetic tests for the private firmware delivery wrapper."""
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "momentum_package", ROOT / "scripts/prepare_momentum_flash_package.py")
firmware = importlib.util.module_from_spec(spec)
spec.loader.exec_module(firmware)


class MomentumPhoneDeliveryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.dist = self.root / "dist" / "f7-C"
        self.updater = self.dist / "f7-update-test"
        self.updater.mkdir(parents=True)
        (self.updater / "update.fuf").write_text(
            "Filetype: Flipper firmware upgrade configuration\n"
            "Version: 2\nTarget: 7\nLoader: updater.bin\nFirmware: firmware.dfu\n")
        (self.updater / "firmware.dfu").write_bytes(b"DFU TEST FIXTURE, NOT FLASHABLE")
        (self.updater / "updater.bin").write_bytes(b"TEST UPDATER, NOT FLASHABLE")
        (self.updater / "resources.tgz").write_bytes(b"TEST RESOURCE FIXTURE")
        self.native = self.dist / "flipper-z-f7-update-test.tgz"
        self.make_native()

    def make_native(self):
        with tarfile.open(self.native, "w:gz") as tar:
            tar.add(self.updater, arcname=self.updater.name)

    def package(self):
        return firmware.build_package(
            self.dist, self.root / "out", "source-test", "momentum-test")

    def test_native_updater_delivered_with_exact_hashes(self):
        output = self.package()
        self.assertEqual(
            firmware.verify_package(output),
            "flipper-z-f7-update-test.tgz")
        with tarfile.open(output, "r:gz") as outer:
            names = {m.name for m in outer.getmembers()}
            self.assertEqual(names, {
                "flipper-z-f7-update-test.tgz",
                "SHA256-manifest.json", "READ_ME_FIRST.txt"})
            records = json.load(outer.extractfile("SHA256-manifest.json"))
            self.assertEqual(records["target"], "Flipper Zero F7")
            self.assertEqual(len(records["files"]), 4)

    def test_reject_updater_changed_after_native_tgz_built(self):
        (self.updater / "firmware.dfu").write_bytes(b"ALTERED")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.package()

    def test_reject_missing_native_tgz(self):
        self.native.unlink()
        with self.assertRaisesRegex(ValueError, "exactly one"):
            self.package()

    def test_reject_wrong_update_target(self):
        (self.updater / "update.fuf").write_text(
            "Filetype: Flipper firmware upgrade configuration\n"
            "Target: 6\nLoader: updater.bin\n")
        self.make_native()
        with self.assertRaisesRegex(ValueError, "format/target"):
            self.package()

    def test_reject_extra_unlisted_file_in_tgz(self):
        extra = self.root / "bad.txt"
        extra.write_text("not in updater folder")
        with tarfile.open(self.native, "w:gz") as tar:
            tar.add(self.updater, arcname=self.updater.name)
            tar.add(extra, arcname="outside/bad.txt")
        with self.assertRaisesRegex(ValueError, "top-level"):
            self.package()

    def test_reject_archive_with_symlink_member(self):
        with tarfile.open(self.native, "w:gz") as tar:
            tar.add(self.updater, arcname=self.updater.name)
            symlink = tarfile.TarInfo(self.updater.name + "/alias")
            symlink.type = tarfile.SYMTYPE
            symlink.linkname = "../other"
            tar.addfile(symlink)
        with self.assertRaisesRegex(ValueError, "links and special"):
            self.package()

    def test_reject_modified_delivery_hash(self):
        output = self.package()
        changed = self.root / "corrupt.tar.gz"
        with tarfile.open(output, "r:gz") as original:
            entries = {
                member.name: original.extractfile(member).read()
                for member in original.getmembers()}
        entries["flipper-z-f7-update-test.tgz"] += b"tampered"
        with tarfile.open(changed, "w:gz") as archive:
            for name, data in entries.items():
                item = tarfile.TarInfo(name)
                item.size = len(data)
                archive.addfile(item, io.BytesIO(data))
        with self.assertRaisesRegex(ValueError, "hash/size"):
            firmware.verify_package(changed)


if __name__ == "__main__":
    unittest.main()
