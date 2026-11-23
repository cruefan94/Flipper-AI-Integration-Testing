"""Public-only CI checks. No private firmware source or credentials required."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class PublicCiTests(unittest.TestCase):
    def test_public_workspace_discloses_source_boundary(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("not copied here", readme)
        self.assertIn("UNTESTED", readme)

    def test_contract_fixture_roundtrip(self):
        packet = {"version": 1, "id": "smoke-001", "type": "diagnostics.request", "payload": {}}
        decoded = json.loads(json.dumps(packet, separators=(",", ":")))
        self.assertEqual(decoded, packet)
        self.assertIsInstance(decoded["payload"], dict)

    def test_infrastructure_is_not_firmware_validation(self):
        workflow = (ROOT / ".github/workflows/public-ci-smoke.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("runs-on: ubuntu-24.04", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("Flipper-AI-Momentum-.git", workflow)


    def test_release_gate_rejects_skipped_native_jobs_and_missing_real_crc(self):
        from scripts.release_evidence_gate import validate_candidate
        record = {
            "kind": "momentum_f7",
            "source_sha": "a" * 40,
            "artifact_sha256": "b" * 64,
            "build_run_url": "https://github.com/example/repo/actions/runs/123",
            "required_jobs": {"firmware": "skipped"},
            "firmware_dfu_sha256": "c" * 64,
            "real_firmware_dfu_crc_verified": False,
            "encrypted_only_delivery": True,
            "qflipper_recovery_documented": True,
        }
        errors = validate_candidate(record)
        self.assertTrue(any("skipped" in x for x in errors))
        self.assertTrue(any("CRC" in x for x in errors))
        record["required_jobs"]["firmware"] = "success"
        record["real_firmware_dfu_crc_verified"] = True
        self.assertEqual(validate_candidate(record), [])

    def test_release_gate_rejects_android_signer_mismatch(self):
        from scripts.release_evidence_gate import validate_candidate
        record = {
            "kind": "android_apk",
            "source_sha": "a" * 40,
            "artifact_sha256": "b" * 64,
            "build_run_url": "https://github.com/example/repo/actions/runs/123",
            "required_jobs": {"apk": "success", "ai1": "success"},
            "signer_cert_sha256": "c" * 64,
            "upgrade_signer_match": False,
            "ble_ai1_contract_passed": True,
        }
        self.assertIn("installed APK signer compatibility unverified", validate_candidate(record))
        record["upgrade_signer_match"] = True
        self.assertEqual(validate_candidate(record), [])

    def test_release_gate_rejects_missing_provenance(self):
        from scripts.release_evidence_gate import validate_candidate
        self.assertIn("exact source SHA missing", validate_candidate({
            "kind": "android_apk", "source_sha": "short", "required_jobs": {"apk": "success"}
        }))

if __name__ == "__main__":
    unittest.main()
