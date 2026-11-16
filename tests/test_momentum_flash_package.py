#!/usr/bin/env python3
"""Public-safe synthetic tests for the private firmware delivery wrapper."""
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "momentum_package", ROOT / "scripts/prepare_momentum_flash_package.py")
firmware = importlib.util.module_from_spec(spec)
spec.loader.exec_module(firmware)


class MomentumPhoneDeliveryTest(unittest.TestCase):
    @staticmethod
    def synthetic_dfu():
        # Synthetic DFU only: correct suffix CRC, not functional firmware.
        payload = b"NOT FLASHABLE: TEST ONLY!" * 5
        suffix_no_crc = struct.pack("<HHHH", 0xFFFF, 0xFFFF, 0x0483, 0x011A) + b"UFD" + bytes([16])
        prefix = payload + suffix_no_crc
        checksum = (zlib.crc32(prefix) ^ 0xFFFFFFFF) & 0xFFFFFFFF
        return prefix + struct.pack("<I", checksum)

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
        (self.updater / "firmware.dfu").write_bytes(self.synthetic_dfu())
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

    def test_reject_invalid_dfu_crc_even_if_tgz_sha_matches(self):
        valid = bytearray((self.updater / "firmware.dfu").read_bytes())
        self.assertEqual(zlib.crc32(valid), 0xFFFFFFFF)
        valid[5] ^= 0x01
        (self.updater / "firmware.dfu").write_bytes(valid)
        self.make_native()
        with self.assertRaisesRegex(ValueError, "DFU file CRC mismatch"):
            self.package()

    def test_reject_invalid_dfu_suffix_even_with_crc_matched(self):
        invalid = bytearray(self.synthetic_dfu())
        invalid[-8:-5] = b"BAD"
        prefix = bytes(invalid[:-4])
        invalid[-4:] = struct.pack("<I", zlib.crc32(prefix) ^ 0xFFFFFFFF)
        (self.updater / "firmware.dfu").write_bytes(invalid)
        self.make_native()
        with self.assertRaisesRegex(ValueError, "DFU firmware suffix"):
            self.package()

    def test_reject_dfu_bad_crc_in_delivery_verify(self):
        """Even coherent outer and inner SHA-256 values cannot mask bad DFU CRC."""
        delivery = self.package()
        with tarfile.open(delivery, "r:gz") as outer:
            entries = {
                member.name: outer.extractfile(member).read()
                for member in outer.getmembers()
            }
        manifest = json.loads(entries["SHA256-manifest.json"])

        # Corrupt the DFU body but keep its UFD suffix and all packaging
        # checksums self-consistent. This mimics a build containing invalid
        # DFU bytes rather than simple damage to a downloaded archive.
        bad_dfu = bytearray(self.synthetic_dfu())
        bad_dfu[5] ^= 0x01
        self.assertNotEqual(zlib.crc32(bad_dfu), 0xFFFFFFFF)
        (self.updater / "firmware.dfu").write_bytes(bad_dfu)
        self.make_native()
        bad_native = self.native.read_bytes()

        manifest["files"]["firmware.dfu"] = {
            "size": len(bad_dfu),
            "sha256": firmware.digest(bytes(bad_dfu)),
        }
        manifest["native_tgz"]["size"] = len(bad_native)
        manifest["native_tgz"]["sha256"] = firmware.digest(bad_native)
        entries["SHA256-manifest.json"] = (
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        ).encode()
        entries[self.native.name] = bad_native
        self.assertEqual(
            firmware.digest(bad_native), manifest["native_tgz"]["sha256"]
        )

        rebuilt = self.root / "coherently-rehashed-bad-dfu.tar.gz"
        with tarfile.open(rebuilt, "w:gz") as archive:
            for name, payload in entries.items():
                item = tarfile.TarInfo(name)
                item.size = len(payload)
                archive.addfile(item, io.BytesIO(payload))

        # Exercise the actual delivery verifier end-to-end, not merely the
        # low-level validate_dfu_crc() helper.
        with self.assertRaisesRegex(ValueError, "DFU file CRC mismatch"):
            firmware.verify_package(rebuilt)

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
