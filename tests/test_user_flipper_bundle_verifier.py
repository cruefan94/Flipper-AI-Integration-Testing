#!/usr/bin/env python3
"""Synthetic public-only tests of the downloadable, private-key-free phone verifier."""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hardware-installer"))
from verify_user_flipper_bundle import REGULAR, verify

SOURCE = "5" * 40
MOMENTUM = "6" * 40
F7 = "Flipper_Update/flipper-z-f7-update-test.tgz"


def native_tgz(target=7):
    contents = {
        "update.fuf": (
            "Filetype: Flipper firmware upgrade configuration\n"
            f"Target: {target}\n"
            "Loader: updater.bin\n"
        ).encode(),
        "updater.bin": b"SYNTHETIC F7 UPDATER",
        "firmware.dfu": b"SYNTHETIC F7 FIRMWARE",
    }
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:gz") as tar:
        for name, blob in contents.items():
            entry = tarfile.TarInfo("f7-update-test/" + name)
            entry.size = len(blob)
            tar.addfile(entry, io.BytesIO(blob))
    return stream.getvalue()


def payload(target=7):
    items = {name: b"TEST-ONLY" for name in REGULAR}
    items.update({
        F7: native_tgz(target),
        "SD_CARD/apps/GPIO/esp_flasher.fap": b"\x7fELF" + b"TEST ONLY",
        "ESP32_WROOM32/firmware.bin": b"\xe9" + b"TEST ONLY",
        "ESP32_WROOM32/bootloader.bin": b"\xe9" + b"TEST ONLY",
        "Licenses/ESP_Flasher_GPL-3.0.txt": b"GNU GENERAL PUBLIC LICENSE - TEST ONLY",
        "READ_ME_FIRST.txt": b"NOT HARDWARE TESTED",
    })
    return items


def pack(path, items, override_manifest=None):
    manifest = {
        "format": "flipper-ai-esp32-complete-candidate-v1",
        "target": "Flipper Zero F7 / classic ESP-WROOM-32 (separate devices)",
        "auto_flash": False,
        "hardware_verified": False,
        "flipper_source_revision": SOURCE,
        "esp32_source_revision": SOURCE,
        "momentum_sdk_revision": MOMENTUM,
        "flasher_upstream_revision": "7" * 40,
        "flasher_patch_revision": "8" * 40,
        "files": {n: {"sha256": hashlib.sha256(d).hexdigest(), "size": len(d)}
                  for n, d in items.items()},
    }
    if override_manifest:
        manifest.update(override_manifest)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for n, d in items.items():
            output.writestr(n, d)
        output.writestr("MANIFEST.json", json.dumps(manifest))
    return path


class UserBundleVerifierTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.bundle = self.root / "candidate.zip"

    def test_valid_bundle_and_opt_in_extraction(self):
        pack(self.bundle, payload())
        name, data = verify(self.bundle, SOURCE)
        self.assertEqual(name, F7)
        self.assertEqual(data["momentum_sdk_revision"], MOMENTUM)
        dest = self.root / "out"
        cmd = [sys.executable, str(ROOT / "hardware-installer/verify_user_flipper_bundle.py"),
               str(self.bundle), "--expect-source", SOURCE, "--extract-flipper", str(dest)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
        self.assertIn("NOT flashed", result.stdout)
        self.assertEqual((dest / Path(F7).name).read_bytes(), self._read_native())
        repeated = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(repeated.returncode, 0)
        self.assertIn("Refusing to overwrite", repeated.stderr)

    def _read_native(self):
        with zipfile.ZipFile(self.bundle) as archive:
            return archive.read(F7)

    def test_wrong_source_is_rejected(self):
        pack(self.bundle, payload())
        with self.assertRaisesRegex(ValueError, "expected private source"):
            verify(self.bundle, "9" * 40)

    def test_damaged_hash_is_rejected(self):
        items = payload()
        records = {n: {"sha256": hashlib.sha256(d).hexdigest(), "size": len(d)}
                   for n, d in items.items()}
        items["ESP32_WROOM32/firmware.bin"] = b"\xe9TAMPERED"
        pack(self.bundle, items, {"files": records})
        with self.assertRaisesRegex(ValueError, "SHA256"):
            verify(self.bundle, SOURCE)

    def test_incorrect_f7_target_is_rejected(self):
        pack(self.bundle, payload(target=6))
        with self.assertRaisesRegex(ValueError, "Wrong Flipper hardware target"):
            verify(self.bundle, SOURCE)

    def test_path_traversal_is_rejected(self):
        items = payload()
        del items["READ_ME_FIRST.txt"]
        items["../READ_ME_FIRST.txt"] = b"NOT TESTED"
        pack(self.bundle, items)
        with self.assertRaises(ValueError):
            verify(self.bundle, SOURCE)

    def test_hardware_verified_flag_is_rejected(self):
        pack(self.bundle, payload(), {"hardware_verified": True})
        with self.assertRaisesRegex(ValueError, "manual-flash"):
            verify(self.bundle, SOURCE)

    def test_fap_missing_elf_magic_is_rejected(self):
        items = payload()
        items["SD_CARD/apps/GPIO/esp_flasher.fap"] = b"NOT AN ELF"
        pack(self.bundle, items)
        with self.assertRaisesRegex(ValueError, "compiled ESP programmer"):
            verify(self.bundle, SOURCE)


if __name__ == "__main__":
    unittest.main()
