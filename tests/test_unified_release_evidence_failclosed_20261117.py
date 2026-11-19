"""Public-safe release-evidence gate. No firmware binaries, private URLs, or credentials.

This validates metadata completeness, not artifact integrity or device readiness.
Real DFU/Android verification must be performed in authorized private jobs.
"""
import re
import unittest

SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")


def validate_release_evidence(record):
    """Return missing/invalid evidence fields; never declare physical success."""
    errors = []
    for component in ("android", "f7"):
        item = record.get(component)
        if not isinstance(item, dict):
            errors.append(f"{component}:missing")
            continue
        if not SHA.fullmatch(str(item.get("source_sha", ""))):
            errors.append(f"{component}:source_sha")
        if not DIGEST.fullmatch(str(item.get("artifact_sha256", ""))):
            errors.append(f"{component}:artifact_sha256")
        if not str(item.get("passing_ci_run_url", "")).startswith(
            "https://github.com/cruefan94/"
        ) or "/actions/runs/" not in str(item.get("passing_ci_run_url", "")):
            errors.append(f"{component}:ci_run")
    android = record.get("android") or {}
    if not android.get("signer_compatibility_verified", False):
        errors.append("android:signer_hold")
    if not android.get("version_upgrade_verified", False):
        errors.append("android:upgrade_hold")
    f7 = record.get("f7") or {}
    for key in ("real_dfu_header_verified", "real_dfu_suffix_crc_verified",
                "encrypted_only_provenance_verified"):
        if not f7.get(key, False):
            errors.append("f7:" + key)
    if not record.get("ai1_exact_revision_parity_verified", False):
        errors.append("ai1:parity_hold")
    if not record.get("physical_device_acceptance", False):
        errors.append("device:hold")
    return errors


class ReleaseEvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.good = {
            "android": {
                "source_sha": "a" * 40, "artifact_sha256": "b" * 64,
                "passing_ci_run_url": "https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/123",
                "signer_compatibility_verified": True, "version_upgrade_verified": True,
            },
            "f7": {
                "source_sha": "c" * 40, "artifact_sha256": "d" * 64,
                "passing_ci_run_url": "https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/456",
                "real_dfu_header_verified": True, "real_dfu_suffix_crc_verified": True,
                "encrypted_only_provenance_verified": True,
            },
            "ai1_exact_revision_parity_verified": True,
            "physical_device_acceptance": True,
        }

    def test_complete_metadata_only(self):
        self.assertEqual(validate_release_evidence(self.good), [])

    def test_missing_firmware_artifact(self):
        self.good.pop("f7")
        self.assertIn("f7:missing", validate_release_evidence(self.good))

    def test_synthetic_crc_cannot_replace_real_crc(self):
        self.good["f7"]["real_dfu_suffix_crc_verified"] = False
        self.good["f7"]["synthetic_crc_passed"] = True
        self.assertIn("f7:real_dfu_suffix_crc_verified", validate_release_evidence(self.good))

    def test_signer_mismatch_holds_upgrade(self):
        self.good["android"]["signer_compatibility_verified"] = False
        self.assertIn("android:signer_hold", validate_release_evidence(self.good))

    def test_ci_green_does_not_imply_device_pass(self):
        self.good["physical_device_acceptance"] = False
        self.assertIn("device:hold", validate_release_evidence(self.good))

    def test_exact_revision_parity_required(self):
        self.good["ai1_exact_revision_parity_verified"] = False
        self.assertIn("ai1:parity_hold", validate_release_evidence(self.good))

    def test_invalid_sha_rejected(self):
        self.good["f7"]["artifact_sha256"] = "not-a-sha"
        self.assertIn("f7:artifact_sha256", validate_release_evidence(self.good))


if __name__ == "__main__":
    unittest.main()
