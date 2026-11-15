#!/usr/bin/env python3
"""Synthetic-only tests for the encrypted one-download Flipper/ESP32 candidate."""
from __future__ import annotations
import hashlib
import io
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import prepare_unified_esp32_release as unified
import prepare_momentum_flash_package as firmware
import prepare_esp_flasher_delivery as flasher

SOURCE="a"*40
MOMENTUM="b"*40
PATCH="c"*40


def tar_add(tar,name,data):
    info=tarfile.TarInfo(name)
    info.size=len(data)
    tar.addfile(info,io.BytesIO(data))


def build_wroom(path,source=SOURCE,bad_image=False):
    data={
        "firmware.bin":(b"\x00" if bad_image else b"\xe9") + b"FZTEST" * 50,
        "bootloader.bin":b"\xe9" + b"TEST_BOOT" * 32,
        "partitions.bin":b"\xaa\x50" * 16,
        "READ_FIRST.txt":(
            f"SOURCE_REVISION={source}\n"
            "BOARD_TARGET=esp32dev (provisional classic ESP-WROOM-32)\n"
            "MOMENTUM=No automatic board flash.\n"
            "RESTRICTION=Not for ESP32-S2, Arduino Uno, or any unverified board.\n"
        ).encode("ascii"),
    }
    data["SHA256SUMS.txt"]="".join(
        hashlib.sha256(blob).hexdigest()+f"  {name}\n"
        for name,blob in data.items()).encode("ascii")
    with tarfile.open(path,"w:gz") as archive:
        for name,blob in data.items():
            tar_add(archive,name,blob)


class UnifiedReleaseCandidateTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.folder=self.root / "dist"/"f7-C"/"f7-update-test"
        self.folder.mkdir(parents=True)
        (self.folder/"update.fuf").write_text(
            "Filetype: Flipper firmware upgrade configuration\n"
            "Version: 2\nTarget: 7\nLoader: updater.bin\nFirmware: firmware.dfu\n")
        for name in ("firmware.dfu","updater.bin","resources.tgz"):
            (self.folder/name).write_bytes((name+" TEST ONLY").encode())
        native=self.folder.parent/"flipper-z-f7-update-test.tgz"
        with tarfile.open(native,"w:gz") as tar:
            tar.add(self.folder,arcname="f7-update-test")
        self.f7=firmware.build_package(self.folder.parent,self.root/"out",SOURCE,MOMENTUM)
        binary=self.root/"esp_flasher.fap"
        binary.write_bytes(b"\x7fELF" + b"FAKE FOR TEST ONLY" * 12)
        license_path=self.root/"LICENSE"
        license_path.write_bytes(b"GNU GENERAL PUBLIC LICENSE\nVersion 3\nSYNTHETIC TEST FIXTURE ONLY")
        self.programmer=flasher.pack(binary,license_path,self.root/"programmer.tar.gz",PATCH,MOMENTUM,SOURCE)
        self.esp=self.root/"esp32.tar.gz"
        build_wroom(self.esp)
        self.output=self.root/unified.BUNDLE_NAME

    def build(self):
        return unified.build(self.f7,self.programmer,self.esp,self.output)

    def test_valid_bundle_stays_separate_and_hashed(self):
        bundle=self.build()
        meta=unified.verify(bundle)
        self.assertEqual(meta["format"],unified.VERSION)
        self.assertEqual(meta["flipper_source_revision"],SOURCE)
        self.assertEqual(meta["esp32_source_revision"],SOURCE)
        self.assertEqual(meta["momentum_sdk_revision"],MOMENTUM)
        self.assertFalse(meta["hardware_verified"])
        self.assertFalse(meta["auto_flash"])
        with zipfile.ZipFile(bundle) as z:
            names=set(z.namelist())
            self.assertIn("Flipper_Update/flipper-z-f7-update-test.tgz",names)
            self.assertIn("SD_CARD/apps/GPIO/esp_flasher.fap",names)
            self.assertIn("ESP32_WROOM32/firmware.bin",names)
            self.assertIn("Licenses/ESP_Flasher_GPL-3.0.txt",names)
            self.assertIn("Docs/ESP_Flasher_SOURCE_PROVENANCE.txt",names)
            self.assertIn("MANIFEST.json",names)
            self.assertIn("READ_ME_FIRST.txt",names)
            self.assertIn(b"No automatic ESP32 flashing",z.read("READ_ME_FIRST.txt"))
        self.assertEqual(len(names),12)

    def test_source_revision_mismatch_is_rejected(self):
        build_wroom(self.esp,source="d"*40)
        with self.assertRaisesRegex(ValueError,"revisions do not match"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_wrong_chip_image_signature_is_rejected(self):
        build_wroom(self.esp,bad_image=True)
        with self.assertRaisesRegex(ValueError,"ESP32 firmware image header"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_refuses_overwriting_existing_bundle(self):
        self.output.write_bytes(b"KEEP ME")
        with self.assertRaisesRegex(ValueError,"Refusing overwrite"):
            self.build()
        self.assertEqual(self.output.read_bytes(),b"KEEP ME")

    def test_bundle_modified_after_generation_is_rejected(self):
        self.build()
        original=self.output
        corrupted=self.root/"changed.zip"
        with zipfile.ZipFile(original) as zsrc, zipfile.ZipFile(corrupted,"w") as zdst:
            for name in zsrc.namelist():
                blob=zsrc.read(name)
                if name=="SD_CARD/apps/GPIO/esp_flasher.fap":
                    blob=b"\x7fELF"+b"BAD_REPLACEMENT"
                zdst.writestr(name,blob)
        with self.assertRaisesRegex(ValueError,"Mismatch in release entry"):
            unified.verify(corrupted)

    def test_duplicate_manifest_entry_is_rejected(self):
        self.build()
        corrupted=self.root/"duplicate.zip"
        with zipfile.ZipFile(self.output) as zsrc,zipfile.ZipFile(corrupted,"w") as zdst:
            for name in zsrc.namelist():
                zdst.writestr(name,zsrc.read(name))
            zdst.writestr("READ_ME_FIRST.txt",b"DUPLICATE WARNING")
        with self.assertRaisesRegex(ValueError,"duplicated"):
            unified.verify(corrupted)

    def test_unexpected_wroom_member_is_rejected(self):
        bad=self.root/"extra-esp32.tar.gz"
        with tarfile.open(self.esp) as s, tarfile.open(bad,"w:gz") as d:
            for m in s.getmembers():
                tar_add(d,m.name,s.extractfile(m).read())
            tar_add(d,"../evil",b"escape")
        with self.assertRaisesRegex(ValueError,"member count"):
            unified.build(self.f7,self.programmer,bad,self.output)


if __name__=="__main__":
    unittest.main()
