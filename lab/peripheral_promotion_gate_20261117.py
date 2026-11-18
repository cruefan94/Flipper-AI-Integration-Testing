"""Offline, public-safe peripheral promotion evidence gate. No network/device I/O."""
import re
import unittest

SHA = re.compile(r"^[0-9a-f]{40}$")
REPO = re.compile(r"^cruefan94/(Flipper-AI-Momentum-|Flipper-AI-Android-Satellite|Flipper-AI-Integration-Testing)$")


def review(record):
    """Return blockers; never authorizes deployment or physical operations."""
    if not isinstance(record, dict):
        return ["record must be an object"]
    errors = []
    if record.get("schema_version") != 1:
        errors.append("unsupported schema")
    if not isinstance(record.get("repository"), str) or not REPO.fullmatch(record["repository"]):
        errors.append("repository not allowlisted")
    if not isinstance(record.get("commit"), str) or not SHA.fullmatch(record["commit"]):
        errors.append("exact commit required")
    if not isinstance(record.get("branch"), str) or not record["branch"].startswith("lab/"):
        errors.append("isolated lab branch required")
    if record.get("ci_status") != "success":
        errors.append("passing exact-commit CI required")
    run = record.get("ci_run_id")
    if type(run) is not int or run <= 0:
        errors.append("valid CI run ID required")
    if record.get("ci_commit") != record.get("commit"):
        errors.append("CI must match exact commit")
    if record.get("physical_tested") is not True:
        errors.append("physical compatibility test required")
    if record.get("safety_reviewed") is not True:
        errors.append("safety review required")
    if record.get("api_contract_verified") is not True:
        errors.append("cross-component API contract required")
    if record.get("owner_install_approval") is not True:
        errors.append("owner installation approval required")
    if any(k in record for k in ("token", "secret", "private_key", "firmware_blob", "device_command")):
        errors.append("sensitive or executable field forbidden")
    return errors


class GateTests(unittest.TestCase):
    def setUp(self):
        self.good = dict(schema_version=1, repository="cruefan94/Flipper-AI-Integration-Testing", branch="lab/synthetic", commit="a"*40, ci_commit="a"*40, ci_status="success", ci_run_id=12345, physical_tested=True, safety_reviewed=True, api_contract_verified=True, owner_install_approval=True)

    def test_synthetic_complete(self): self.assertEqual(review(self.good), [])
    def test_non_object(self): self.assertTrue(review(None))
    def test_missing_ci(self): self.assertTrue(review({**self.good, "ci_status":"unknown"}))
    def test_missing_run(self): self.assertTrue(review({**self.good, "ci_run_id":None}))
    def test_bool_run(self): self.assertTrue(review({**self.good, "ci_run_id":True}))
    def test_mismatched_commit(self): self.assertTrue(review({**self.good, "ci_commit":"b"*40}))
    def test_short_sha(self): self.assertTrue(review({**self.good, "commit":"abc"}))
    def test_wrong_branch(self): self.assertTrue(review({**self.good, "branch":"main"}))
    def test_wrong_repo(self): self.assertTrue(review({**self.good, "repository":"someone/other"}))
    def test_unverified_hardware(self): self.assertTrue(review({**self.good, "physical_tested":False}))
    def test_missing_safety(self): self.assertTrue(review({**self.good, "safety_reviewed":False}))
    def test_missing_contract(self): self.assertTrue(review({**self.good, "api_contract_verified":False}))
    def test_missing_approval(self): self.assertTrue(review({**self.good, "owner_install_approval":False}))
    def test_secret_field(self): self.assertTrue(review({**self.good, "token":"fake"}))
    def test_command_field(self): self.assertTrue(review({**self.good, "device_command":"noop"}))
    def test_schema(self): self.assertTrue(review({**self.good, "schema_version":2}))

if __name__ == "__main__":
    unittest.main()
