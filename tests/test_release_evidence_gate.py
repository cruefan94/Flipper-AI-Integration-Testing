"""Offline regression tests for release evidence admission. Synthetic values only."""
import unittest
from tools.release_evidence_gate import validate

def sample(kind="android_apk"):
    r = dict(repository="cruefan94/Flipper-AI-Android-Satellite",
             source_sha="a"*40, workflow_run_id=123,
             workflow_url="https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/123",
             artifact_sha256="b"*64, artifact_kind=kind, ci_result="pass",
             ai1_contract="pass", device_test="pass", signing_match=True,
             version_increment=True, failed_run_ids=[])
    if kind == "f7_updater":
        r.update(repository="cruefan94/Flipper-AI-Momentum-",
                 workflow_url="https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/123",
                 dfu_crc_valid=True, internal_hashes_valid=True,
                 encrypted_only=True, recovery_ready=True)
    return r

class EvidenceTests(unittest.TestCase):
    def test_synthetic_complete_android(self):
        self.assertEqual(validate(sample()), [])
    def test_synthetic_complete_f7(self):
        self.assertEqual(validate(sample("f7_updater")), [])
    def test_unknown_field_rejected(self):
        r=sample();r["private_token"]="secret";self.assertTrue(validate(r))
    def test_missing_signature_rejected(self):
        r=sample();r["signing_match"]=False;self.assertTrue(validate(r))
    def test_f7_crc_rejected(self):
        r=sample("f7_updater");r["dfu_crc_valid"]=False;self.assertTrue(validate(r))
    def test_missing_physical_test_rejected(self):
        r=sample();r["device_test"]="unknown";self.assertTrue(validate(r))
    def test_cross_repo_run_rejected(self):
        r=sample();r["workflow_url"]="https://github.com/other/repo/actions/runs/123";self.assertTrue(validate(r))
    def test_two_failure_requires_proven_fallback(self):
        r=sample();r["failed_run_ids"]=[10,11];self.assertTrue(validate(r))
        r.update(fallback_run_id=12,fallback_result="pass",private_actions_access="accessible")
        self.assertEqual(validate(r),[])
    def test_blocked_private_access_fails_closed(self):
        r=sample();r.update(failed_run_ids=[10,11],fallback_run_id=12,
                            fallback_result="pass",private_actions_access="blocked")
        self.assertTrue(validate(r))
    def test_invalid_sha_rejected(self):
        r=sample();r["source_sha"]="not-a-sha";self.assertTrue(validate(r))
    def test_boolean_run_id_rejected(self):
        r=sample();r["workflow_run_id"]=True;self.assertTrue(validate(r))

if __name__ == "__main__":
    unittest.main()
