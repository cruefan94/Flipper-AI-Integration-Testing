import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("gate", Path(__file__).resolve().parents[1] / "tools" / "f7_release_evidence_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

BASE = dict(source_sha="a"*40, native_run_url="https://github.com/example/private/actions/runs/123",
    native_build_passed=True, native_job_not_skipped=True, real_dfu_crc_verified=True,
    native_updater_sha256="b"*64, encrypted_artifact_only=True,
    flash_layout_safety_passed=True, android_signing_compatible=True,
    android_version_code_increases=True, paired_ai1_contract_passed=True,
    hardware_verified=True, owner_flash_approved=True)

class EvidenceGateTests(unittest.TestCase):
    def test_full_declaration_passes_policy_only(self):
        self.assertEqual([], gate.validate(BASE))
    def test_missing_evidence_fails(self):
        for key in BASE:
            with self.subTest(key=key):
                d = BASE.copy()
                del d[key]
                self.assertTrue(gate.validate(d))
    def test_false_and_strings_do_not_pass(self):
        for key in gate.REQUIRED[2:]:
            if key == "native_updater_sha256":
                continue
            for value in (False, "true", 1, None):
                with self.subTest(key=key, value=value):
                    d = BASE.copy()
                    d[key] = value
                    self.assertTrue(gate.validate(d))
    def test_invalid_hashes_and_run_urls(self):
        for key, value in (("source_sha", "a"*39), ("native_updater_sha256", "b"*63),
                           ("native_run_url", "https://example.com/123"),
                           ("native_run_url", "https://github.com/x/y/actions/runs/123?token=secret")):
            with self.subTest(key=key):
                d = BASE.copy()
                d[key] = value
                self.assertTrue(gate.validate(d))
    def test_no_non_object(self):
        self.assertTrue(gate.validate([]))

if __name__ == "__main__":
    unittest.main()
