"""Hardware-free tests for the sanitized AI1 candidate metadata parity gate."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from verify_ai1_candidate_pair import check_pair


def record(component):
    firmware = component == "firmware"
    return {
        "component": component,
        "source_repo": "cruefan94/Flipper-AI-Momentum-" if firmware else "cruefan94/Flipper-AI-Android-Satellite",
        "source_commit": "a" * 40,
        "ai1_contract_sha256": "b" * 64,
        "ai1_protocol_version": "1.0",
        "artifact_sha256": "c" * 64,
        "artifact_kind": "f7-updater-tgz" if firmware else "android-test-apk",
        "ci_run_url": "https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328",
    }


class CandidatePairTests(unittest.TestCase):
    def setUp(self):
        self.firmware, self.android = record("firmware"), record("android")

    def test_matching_sanitized_metadata_is_not_release_approval(self):
        self.assertIn("METADATA_PARITY_ONLY", check_pair(self.firmware, self.android))

    def test_contract_digest_mismatch(self):
        self.android["ai1_contract_sha256"] = "d" * 64
        with self.assertRaisesRegex(ValueError, "mismatch"):
            check_pair(self.firmware, self.android)

    def test_protocol_version_mismatch(self):
        self.android["ai1_protocol_version"] = "2.0"
        with self.assertRaisesRegex(ValueError, "mismatch"):
            check_pair(self.firmware, self.android)

    def test_cross_deliverable_source_spoof(self):
        self.android["source_repo"] = self.firmware["source_repo"]
        with self.assertRaisesRegex(ValueError, "ownership"):
            check_pair(self.firmware, self.android)

    def test_extra_secret_field_rejected(self):
        self.android["device_token"] = "placeholder"
        with self.assertRaisesRegex(ValueError, "unexpected"):
            check_pair(self.firmware, self.android)

    def test_bad_hash_rejected(self):
        self.firmware["artifact_sha256"] = "unknown"
        with self.assertRaisesRegex(ValueError, "artifact_sha256"):
            check_pair(self.firmware, self.android)

    def test_untrusted_ci_url_rejected(self):
        self.android["ci_run_url"] = "https://example.invalid/actions/runs/123"
        with self.assertRaisesRegex(ValueError, "CI run URL"):
            check_pair(self.firmware, self.android)


if __name__ == "__main__":
    unittest.main()
