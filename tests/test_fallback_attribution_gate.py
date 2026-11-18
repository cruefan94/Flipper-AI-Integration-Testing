"""Public-safe fallback attribution gate. Metadata only; no GitHub access or secrets."""
import unittest

REQUIRED = ("source_repo", "workflow", "branch", "failed_run_ids",
            "fallback_run_id", "fallback_component", "fallback_conclusion")

def assess(record):
    """Fail closed unless an executed fallback is attributable to two failures."""
    if not isinstance(record, dict) or any(not record.get(k) for k in REQUIRED):
        return "BLOCKED"
    failures = record["failed_run_ids"]
    if not isinstance(failures, list) or len(failures) < 2:
        return "BLOCKED"
    if any(not isinstance(i, int) or isinstance(i, bool) or i <= 0 for i in failures):
        return "BLOCKED"
    if failures[-1] == failures[-2] or not isinstance(record["fallback_run_id"], int):
        return "BLOCKED"
    if record["fallback_run_id"] <= 0 or isinstance(record["fallback_run_id"], bool):
        return "BLOCKED"
    if record["fallback_conclusion"] != "success":
        return "BLOCKED"
    if record["fallback_component"] not in ("firmware", "android", "protocol", "contract", "diagnostic"):
        return "BLOCKED"
    if record.get("trigger_source_run_id") != failures[-1]:
        return "UNATTRIBUTED"
    if record.get("trigger_branch") != record["branch"] or record.get("trigger_workflow") != record["workflow"]:
        return "UNATTRIBUTED"
    if record.get("trigger_source_repo") != record["source_repo"]:
        return "UNATTRIBUTED"
    if record.get("fallback_job_conclusion") != "success":
        return "BLOCKED"
    return "ATTRIBUTED_TEST_ONLY"

class AttributionTests(unittest.TestCase):
    def setUp(self):
        self.record = dict(source_repo="private/repo", workflow="inventory",
            branch="fix/safe", failed_run_ids=[100, 101], fallback_run_id=200,
            fallback_component="firmware", fallback_conclusion="success",
            trigger_source_run_id=101, trigger_branch="fix/safe",
            trigger_workflow="inventory", trigger_source_repo="private/repo",
            fallback_job_conclusion="success")

    def test_complete_evidence_is_test_only(self):
        self.assertEqual(assess(self.record), "ATTRIBUTED_TEST_ONLY")

    def test_missing_trigger_is_unattributed(self):
        self.record.pop("trigger_source_run_id")
        self.assertEqual(assess(self.record), "UNATTRIBUTED")

    def test_wrong_branch_is_unattributed(self):
        self.record["trigger_branch"] = "another"
        self.assertEqual(assess(self.record), "UNATTRIBUTED")

    def test_skipped_job_is_blocked(self):
        self.record["fallback_job_conclusion"] = "skipped"
        self.assertEqual(assess(self.record), "BLOCKED")

    def test_one_failure_is_blocked(self):
        self.record["failed_run_ids"] = [101]
        self.assertEqual(assess(self.record), "BLOCKED")

    def test_duplicate_failure_is_blocked(self):
        self.record["failed_run_ids"] = [101, 101]
        self.assertEqual(assess(self.record), "BLOCKED")

    def test_missing_private_permission_is_blocked(self):
        self.record["fallback_run_id"] = None
        self.assertEqual(assess(self.record), "BLOCKED")

    def test_android_skipped_cannot_use_firmware_pass(self):
        self.record["fallback_component"] = "android"
        self.record["fallback_job_conclusion"] = "skipped"
        self.assertEqual(assess(self.record), "BLOCKED")

if __name__ == "__main__":
    unittest.main()
