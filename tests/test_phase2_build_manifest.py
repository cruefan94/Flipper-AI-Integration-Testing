"""Offline, synthetic tests for fail-closed build artifact evidence."""
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("phase2_evidence", ROOT / "scripts/phase2_build_manifest.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SHA = "a" * 40
REPO = "cruefan94/Flipper-AI-Android-Satellite"


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "artifacts").mkdir()
        (self.root / "artifacts/app.apk").write_bytes(b"synthetic-fixture-only")
        self.manifest = self.root / "evidence.json"

    def build(self):
        MODULE.write(self.root, self.manifest, REPO, SHA, "android-apk", ["artifacts/app.apk"])

    def test_round_trip_explicitly_not_hardware_verified(self):
        self.build()
        data = MODULE.verify(self.root, self.manifest, SHA)
        self.assertEqual(data["scope"], "build-artifact-only")
        self.assertEqual(data["repository"], REPO)
        self.assertEqual(data["artifacts"][0]["bytes"], 22)

    def test_tampered_artifact_fails(self):
        self.build()
        (self.root / "artifacts/app.apk").write_bytes(b"tampered")
        with self.assertRaises(MODULE.EvidenceError):
            MODULE.verify(self.root, self.manifest)

    def test_expected_sha_must_match(self):
        self.build()
        with self.assertRaises(MODULE.EvidenceError):
            MODULE.verify(self.root, self.manifest, "b" * 40)

    def test_source_sha_rejects_partial_and_non_hex(self):
        for bad in ("abc123", "z" * 40, "A" * 40):
            with self.subTest(bad=bad), self.assertRaises(MODULE.EvidenceError):
                MODULE.write(self.root, self.manifest, REPO, bad, "android-apk", ["artifacts/app.apk"])

    def test_unsafe_paths_and_duplicates_rejected(self):
        for bad in ("../outside.apk", "/etc/passwd", "artifacts/../artifacts/app.apk",
                    "artifacts\\app.apk", "./artifacts/app.apk"):
            with self.subTest(bad=bad), self.assertRaises(MODULE.EvidenceError):
                MODULE.write(self.root, self.manifest, REPO, SHA, "android-apk", [bad])
        with self.assertRaises(MODULE.EvidenceError):
            MODULE.write(self.root, self.manifest, REPO, SHA, "android-apk",
                         ["artifacts/app.apk", "artifacts/app.apk"])

    def test_symlink_escape_rejected(self):
        outside = self.root / "artifacts-link"
        outside.symlink_to(self.root / "artifacts", target_is_directory=True)
        with self.assertRaises(MODULE.EvidenceError):
            MODULE.write(self.root, self.manifest, REPO, SHA, "android-apk",
                         ["artifacts-link/app.apk"])

    def test_modified_manifest_and_false_hardware_scope_rejected(self):
        self.build()
        data = json.loads(self.manifest.read_text())
        data["scope"] = "hardware-verified"
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(MODULE.EvidenceError):
            MODULE.verify(self.root, self.manifest)

    def test_missing_or_duplicate_manifest_records_rejected(self):
        self.build()
        data = json.loads(self.manifest.read_text())
        data["artifacts"] *= 2
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(MODULE.EvidenceError):
            MODULE.verify(self.root, self.manifest)
        data["artifacts"] = []
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(MODULE.EvidenceError):
            MODULE.verify(self.root, self.manifest)


if __name__ == "__main__":
    unittest.main()
