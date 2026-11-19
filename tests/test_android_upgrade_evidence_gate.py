#!/usr/bin/env python3
"""Public-safe Android APK release evidence gate. No APKs, keys or device data."""
import unittest


def evaluate(e):
    """Return missing release proofs; metadata is not proof until independently verified."""
    failures = []
    if not isinstance(e, dict):
        return ["missing evidence object"]
    required = ("source_sha", "build_run_url", "artifact_sha256", "package_id",
                "candidate_version_code", "installed_version_code",
                "signer_matches_installed", "build_job_executed",
                "build_job_conclusion", "ai1_contract_verified")
    for field in required:
        if field not in e:
            failures.append("missing " + field)
    if failures:
        return failures
    for field in ("source_sha", "artifact_sha256"):
        val = e[field]
        if not isinstance(val, str) or len(val) != (40 if field == "source_sha" else 64) or any(c not in "0123456789abcdef" for c in val.lower()):
            failures.append("invalid " + field)
    if not isinstance(e["build_run_url"], str) or not e["build_run_url"].startswith("https://github.com/") or "/actions/runs/" not in e["build_run_url"]:
        failures.append("invalid build run URL")
    if not isinstance(e["package_id"], str) or not e["package_id"].startswith("com."):
        failures.append("invalid package ID")
    for field in ("candidate_version_code", "installed_version_code"):
        if type(e[field]) is not int or e[field] < 1:
            failures.append("invalid " + field)
    if type(e["candidate_version_code"]) is int and type(e["installed_version_code"]) is int and e["candidate_version_code"] <= e["installed_version_code"]:
        failures.append("versionCode is not an upgrade")
    if e["signer_matches_installed"] is not True:
        failures.append("installed signer compatibility not verified")
    if e["build_job_executed"] is not True or e["build_job_conclusion"] != "success":
        failures.append("APK build job did not execute successfully")
    if e["ai1_contract_verified"] is not True:
        failures.append("paired AI1 contract not verified")
    return failures


class UpgradeEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.good = dict(source_sha="a"*40, artifact_sha256="b"*64,
                         build_run_url="https://github.com/example/project/actions/runs/123",
                         package_id="com.example.satellite", candidate_version_code=12,
                         installed_version_code=11, signer_matches_installed=True,
                         build_job_executed=True, build_job_conclusion="success",
                         ai1_contract_verified=True)

    def test_complete_evidence(self):
        self.assertEqual(evaluate(self.good), [])

    def test_missing_signer(self):
        e = {**self.good, "signer_matches_installed": None}
        self.assertIn("installed signer compatibility not verified", evaluate(e))

    def test_mismatched_signer(self):
        e = {**self.good, "signer_matches_installed": False}
        self.assertTrue(evaluate(e))

    def test_equal_version(self):
        e = {**self.good, "candidate_version_code": 11}
        self.assertIn("versionCode is not an upgrade", evaluate(e))

    def test_downgrade(self):
        e = {**self.good, "candidate_version_code": 10}
        self.assertTrue(evaluate(e))

    def test_skipped_build(self):
        e = {**self.good, "build_job_executed": False}
        self.assertTrue(evaluate(e))

    def test_missing_artifact_hash(self):
        e = {**self.good, "artifact_sha256": ""}
        self.assertTrue(evaluate(e))

    def test_missing_contract(self):
        e = {**self.good, "ai1_contract_verified": False}
        self.assertTrue(evaluate(e))

    def test_boolean_version_rejected(self):
        e = {**self.good, "candidate_version_code": True}
        self.assertTrue(evaluate(e))

    def test_no_evidence(self):
        self.assertTrue(evaluate(None))


if __name__ == "__main__":
    unittest.main()
