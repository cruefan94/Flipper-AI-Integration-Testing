#!/usr/bin/env python3
"""Public synthetic-only tests for the pinned audited phone-side F7 extractor."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from unittest import mock
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "termux"))
import audited_f7_to_downloads as candidate

PKG_SPEC = importlib.util.spec_from_file_location(
    "native_f7_package", ROOT / "scripts/prepare_momentum_flash_package.py")
package = importlib.util.module_from_spec(PKG_SPEC)
PKG_SPEC.loader.exec_module(package)
TEST_PASSPHRASE = "PUBLIC-TEST-ONLY-PASSPHRASE"


class AuditedF7PhoneTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.downloads = self.root / "Android-Download"
        self.downloads.mkdir()
        self.outer = self.downloads / (candidate.ARTIFACT_STEM + ".zip")

    def make_artifact(self, source=None, *, extra_outer=None):
        source = candidate.SOURCE_REVISION if source is None else source
        dist = self.root / "dist" / "f7-C"
        updater = dist / "f7-update-synthetic"
        updater.mkdir(parents=True, exist_ok=True)
        (updater / "update.fuf").write_text(
            "Filetype: Flipper firmware upgrade configuration\n"
            "Target: 7\nLoader: updater.bin\nFirmware: firmware.dfu\n")
        (updater / "updater.bin").write_bytes(b"UNFLASHABLE TEST UPDATER")
        (updater / "firmware.dfu").write_bytes(b"UNFLASHABLE TEST F7 DATA")
        native = dist / "flipper-z-f7-update-test-fixture.tgz"
        with tarfile.open(native, "w:gz") as tgz:
            tgz.add(updater, arcname="f7-update-synthetic")
        wrapper = package.build_package(dist, self.root / "stage", source, "6" * 40)
        encrypted = self.root / candidate.ENCRYPTED_NAME
        env = os.environ.copy()
        env["TEST_ONLY_PASS"] = TEST_PASSPHRASE
        subprocess.run(
            ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", "250000",
             "-salt", "-pass", "env:TEST_ONLY_PASS", "-in", str(wrapper),
             "-out", str(encrypted)],
            check=True, capture_output=True, timeout=20, env=env)
        with zipfile.ZipFile(self.outer, "w", zipfile.ZIP_STORED) as z:
            z.write(encrypted, candidate.ENCRYPTED_NAME)
            if extra_outer is not None:
                z.writestr(extra_outer, b"invalid extra")
        return native.read_bytes(), encrypted

    def test_outer_digest_and_exact_inventory(self):
        blob, _ = self.make_artifact()
        digest = candidate.file_digest(self.outer)
        with tempfile.TemporaryDirectory() as tmp:
            name = candidate.extract_encrypted_from_outer_zip(
                self.outer, Path(tmp), expected_digest=digest)
            self.assertEqual(name.name, candidate.ENCRYPTED_NAME)
            self.assertGreater(name.stat().st_size, 1000)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(candidate.DeliveryError, "SHA-256 mismatch"):
                candidate.extract_encrypted_from_outer_zip(
                    self.outer, Path(tmp), expected_digest="0" * 64)

    def test_reject_extra_outer_members(self):
        self.make_artifact(extra_outer="ESP32_WROOM32/firmware.bin")
        digest = candidate.file_digest(self.outer)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(candidate.DeliveryError, "Wrong artifact contents"):
                candidate.extract_encrypted_from_outer_zip(
                    self.outer, Path(tmp), expected_digest=digest)

    def test_real_openssl_and_full_native_verification_to_downloads(self):
        blob, _ = self.make_artifact()
        with mock.patch.object(candidate, "ARTIFACT_DIGEST", candidate.file_digest(self.outer)), \
             mock.patch("builtins.input", return_value=TEST_PASSPHRASE), \
             mock.patch("sys.stdin.isatty", return_value=True):
            result = candidate.execute(self.downloads, self.outer, visible=True)
            self.assertEqual(result.read_bytes(), blob)
            self.assertTrue(result.name.startswith("flipper-z-f7-update-"))
            # Another run preserves an identical existing .tgz.
            result2 = candidate.execute(self.downloads, self.outer, visible=True)
            self.assertEqual(result2, result)

    def test_source_revision_pin_rejects_other_valid_firmware(self):
        self.make_artifact(source="a" * 40)
        with mock.patch.object(candidate, "ARTIFACT_DIGEST", candidate.file_digest(self.outer)), \
             mock.patch("builtins.input", return_value=TEST_PASSPHRASE), \
             mock.patch("sys.stdin.isatty", return_value=True):
            with self.assertRaisesRegex(candidate.DeliveryError, "Wrong firmware source"):
                candidate.execute(self.downloads, self.outer, visible=True)
        self.assertFalse(list(self.downloads.glob("*.tgz")))

    def test_no_overwrite_of_existing_different_firmware(self):
        with self.assertRaisesRegex(candidate.DeliveryError, "older/different"):
            target = self.downloads / "flipper-z-f7-update-test.tgz"
            target.write_bytes(b"known-good-preserve")
            candidate.save_verified_to_downloads(
                self.downloads, target.name, b"new")
        self.assertEqual(target.read_bytes(), b"known-good-preserve")

    def test_cannot_select_combined_archive(self):
        combined = self.downloads / "FlipperAI_ESP32_Complete_Flash_Candidate_UNTESTED.zip"
        combined.write_bytes(b"UNTESTABLE")
        with self.assertRaisesRegex(candidate.DeliveryError, "Wrong file"):
            candidate.execute(self.downloads, combined, visible=True)

    def test_detect_unambiguous_download(self):
        self.make_artifact()
        self.assertEqual(candidate.identify_input(None, self.downloads), self.outer)

    def test_encrypted_standalone_is_checked_by_manifest_and_source_pin(self):
        native, encrypted = self.make_artifact()
        copied = self.downloads / candidate.ENCRYPTED_NAME
        copied.write_bytes(encrypted.read_bytes())
        with mock.patch("builtins.input", return_value=TEST_PASSPHRASE), \
             mock.patch("sys.stdin.isatty", return_value=True):
            output = candidate.execute(self.downloads, copied, visible=True)
        self.assertEqual(output.read_bytes(), native)


if __name__ == "__main__":
    unittest.main()
