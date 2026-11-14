#!/usr/bin/env python3
"""Synthetic non-hardware tests of Termux local F7 firmware package extraction."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("firmware_to_phone", HERE / "firmware_to_phone.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class NativeFirmwareTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.folder = "f7-update-local-test"
        self.filename = "flipper-z-f7-update-local-test.tgz"
        self.files = {
            "update.fuf": b"Filetype: Flipper firmware upgrade configuration\nVersion: 2\n"
                          b"Target: 7\nLoader: updater.bin\nFirmware: firmware.dfu\n",
            "firmware.dfu": b"synthetic only, not a real DFU",
            "updater.bin": b"synthetic loader not flashable",
            "resources.tgz": b"synthetic resource",
        }
        self.make_delivery()

    @staticmethod
    def add(tar, name, data):
        member = tarfile.TarInfo(name)
        member.size = len(data)
        tar.addfile(member, io.BytesIO(data))

    def make_delivery(self, native_override=None, manifest_changes=None, extra=None):
        with io.BytesIO() as buf:
            with tarfile.open(fileobj=buf, mode="w:gz") as native_tar:
                for path, data in self.files.items():
                    self.add(native_tar, self.folder + "/" + path, data)
            native = native_override if native_override is not None else buf.getvalue()

        manifest = {
            "format": module.FORMAT,
            "target": "Flipper Zero F7",
            "source_revision": "unit-test-only",
            "updater": self.folder,
            "files": {k: {"size": len(v), "sha256": sha(v)} for k, v in self.files.items()},
            "native_tgz": {
                "name": self.filename, "size": len(native), "sha256": sha(native),
            },
        }
        if manifest_changes:
            manifest.update(manifest_changes)
        self.outer = self.root / "firmware-delivery.tar.gz"
        with tarfile.open(self.outer, "w:gz") as archive:
            self.add(archive, self.filename, native)
            self.add(archive, "SHA256-manifest.json", json.dumps(manifest).encode())
            self.add(archive, "READ_ME_FIRST.txt", b"synthetic test fixture; DO NOT FLASH")
            if extra:
                self.add(archive, extra, b"unexpected")

    def test_valid_native_f7_candidate(self):
        name, data, source = module.verify_delivery(self.outer)
        self.assertEqual(name, self.filename)
        self.assertGreater(len(data), 60)
        self.assertEqual(source, "unit-test-only")

    def test_target_must_be_flipper_f7(self):
        self.make_delivery(manifest_changes={"target": "Flipper Zero F6"})
        with self.assertRaisesRegex(module.DeliveryError, "hardware target"):
            module.verify_delivery(self.outer)

    def test_native_checksum_is_checked(self):
        self.make_delivery(manifest_changes={"native_tgz": {
            "name": self.filename, "size": 7, "sha256": "0" * 64
        }})
        with self.assertRaisesRegex(module.DeliveryError, "checksum mismatch"):
            module.verify_delivery(self.outer)

    def test_fuf_target_must_match(self):
        self.files["update.fuf"] = self.files["update.fuf"].replace(b"Target: 7", b"Target: 6")
        self.make_delivery()
        with self.assertRaisesRegex(module.DeliveryError, "target/loader mismatch"):
            module.verify_delivery(self.outer)

    def test_native_firmware_contents_checked(self):
        self.make_delivery(manifest_changes={"files": {
            k: {"size": len(v), "sha256": "0" * 64} for k, v in self.files.items()
        }})
        with self.assertRaisesRegex(module.DeliveryError, "Native firmware manifest mismatch"):
            module.verify_delivery(self.outer)

    def test_unknown_outer_member_rejected(self):
        self.make_delivery(extra="invalid-content.txt")
        with self.assertRaisesRegex(module.DeliveryError, "unexpected files"):
            module.verify_delivery(self.outer)

    def test_unsafe_tar_entry_rejected(self):
        with io.BytesIO() as buf:
            with tarfile.open(fileobj=buf, mode="w:gz") as native_tar:
                for name, data in self.files.items():
                    self.add(native_tar, self.folder + "/" + name, data)
                symlink = tarfile.TarInfo(self.folder + "/escape")
                symlink.type = tarfile.SYMTYPE
                symlink.linkname = "/etc/passwd"
                native_tar.addfile(symlink)
            self.make_delivery(native_override=buf.getvalue())
        with self.assertRaisesRegex(module.DeliveryError, "link or unsupported special"):
            module.verify_delivery(self.outer)

    def test_safe_local_save_and_collision(self):
        name, data, _ = module.verify_delivery(self.outer)
        target = module.save_candidate(self.root / "saved", name, data)
        self.assertTrue(target.is_file())
        self.assertEqual(target.read_bytes(), data)
        self.assertEqual(module.save_candidate(self.root / "saved", name, data), target)
        target.write_bytes(b"different")
        next_target = module.save_candidate(self.root / "saved", name, data)
        self.assertNotEqual(next_target, target)
        self.assertEqual(next_target.read_bytes(), data)

    def test_latest_successful_main_run_selected(self):
        runs = [
            {"id": 7, "created_at": "2026-11-14T05:20:00Z", "name": module.WORKFLOW_NAME,
             "head_branch": "main", "conclusion": "failure", "status": "completed"},
            {"id": 6, "created_at": "2026-11-14T05:15:00Z", "name": module.WORKFLOW_NAME,
             "head_branch": "feature/exp", "conclusion": "success", "status": "completed"},
            {"id": 5, "created_at": "2026-11-14T05:10:00Z", "name": module.WORKFLOW_NAME,
             "head_branch": "main", "conclusion": "success", "status": "completed"},
        ]
        def fake_api(path):
            if path.endswith("actions/runs?per_page=50"):
                return {"workflow_runs": runs}
            if path.endswith("/runs/5/artifacts?per_page=100"):
                return {"artifacts": [{"id": 42, "name": module.ARTIFACT_NAME, "expired": False}]}
            raise AssertionError("Unexpected GitHub call " + path)
        with patch.object(module, "github", side_effect=fake_api):
            self.assertEqual(module.find_successful_run(), (5, 42))

    def test_expired_artifact_rejected(self):
        with patch.object(module, "github", side_effect=[
            {"id": 5, "name": module.WORKFLOW_NAME, "status": "completed",
             "head_branch": "main", "conclusion": "success"},
            {"artifacts": [{"id": 42, "name": module.ARTIFACT_NAME, "expired": True}]},
        ]):
            with self.assertRaisesRegex(module.DeliveryError, "non-expired"):
                module.find_successful_run(5)

    def test_wrong_explicit_run_rejected(self):
        with patch.object(module, "github", return_value={
            "id": 9, "name": "Unrelated CI", "status": "completed",
            "head_branch": "main", "conclusion": "success",
        }):
            with self.assertRaisesRegex(module.DeliveryError, "not a successful"):
                module.find_successful_run(9)


if __name__ == "__main__":
    unittest.main()
