"""Public-safe, read-only CI failure grouping checks.

This module does not access GitHub, dispatch workflows, or handle private logs.
It deliberately requires the SAME repository, branch and workflow before
classifying two completed failures as a consecutive-failure fallback trigger.
"""
import unittest


def classify_failure_pair(first, second):
    """Return a sanitized decision; never treat cross-workflow failures as a pair."""
    allowed = {"repo", "branch", "workflow", "run_id", "status", "conclusion", "job_provisioned"}
    for run in (first, second):
        if not isinstance(run, dict) or set(run) != allowed:
            return "BLOCKED_INSUFFICIENT_EVIDENCE"
        if any(not isinstance(run[k], str) or not run[k] for k in ("repo", "branch", "workflow")):
            return "BLOCKED_INSUFFICIENT_EVIDENCE"
        if not isinstance(run["run_id"], int) or isinstance(run["run_id"], bool) or run["run_id"] <= 0:
            return "BLOCKED_INSUFFICIENT_EVIDENCE"
        if type(run["job_provisioned"]) is not bool:
            return "BLOCKED_INSUFFICIENT_EVIDENCE"
    if first["run_id"] == second["run_id"]:
        return "BLOCKED_INSUFFICIENT_EVIDENCE"
    if any(first[k] != second[k] for k in ("repo", "branch", "workflow")):
        return "NOT_SAME_WORKFLOW_BRANCH"
    if first["status"] != "completed" or second["status"] != "completed":
        return "WAIT_FOR_COMPLETION"
    if first["conclusion"] != "failure" or second["conclusion"] != "failure":
        return "NO_TWO_FAILURE_TRIGGER"
    if not first["job_provisioned"] and not second["job_provisioned"]:
        return "REPEATED_PRE_PROVISION_FAILURE_REVIEW"
    return "TWO_FAILURE_TRIGGER_REQUIRES_AUTHORIZED_SAFE_DISPATCH"


class PairTests(unittest.TestCase):
    def setUp(self):
        self.a = dict(repo="cruefan94/Flipper-AI-Android-Satellite", branch="test/worker",
                      workflow="Android APK", run_id=43942738536, status="completed",
                      conclusion="failure", job_provisioned=True)
        self.b = dict(self.a, run_id=43942738619)

    def test_same_workflow_two_failures(self):
        self.assertEqual(classify_failure_pair(self.a, self.b),
                         "TWO_FAILURE_TRIGGER_REQUIRES_AUTHORIZED_SAFE_DISPATCH")

    def test_different_workflows_are_not_consecutive(self):
        self.b["workflow"] = "Android side-by-side APK"
        self.assertEqual(classify_failure_pair(self.a, self.b), "NOT_SAME_WORKFLOW_BRANCH")

    def test_different_branch(self):
        self.b["branch"] = "test/other"
        self.assertEqual(classify_failure_pair(self.a, self.b), "NOT_SAME_WORKFLOW_BRANCH")

    def test_preprovision_repeat(self):
        self.a["job_provisioned"] = False
        self.b["job_provisioned"] = False
        self.assertEqual(classify_failure_pair(self.a, self.b), "REPEATED_PRE_PROVISION_FAILURE_REVIEW")

    def test_pending(self):
        self.b["status"] = "in_progress"
        self.assertEqual(classify_failure_pair(self.a, self.b), "WAIT_FOR_COMPLETION")

    def test_missing_metadata(self):
        del self.b["workflow"]
        self.assertEqual(classify_failure_pair(self.a, self.b), "BLOCKED_INSUFFICIENT_EVIDENCE")

    def test_duplicate_run(self):
        self.b["run_id"] = self.a["run_id"]
        self.assertEqual(classify_failure_pair(self.a, self.b), "BLOCKED_INSUFFICIENT_EVIDENCE")

    def test_success_breaks_pair(self):
        self.b["conclusion"] = "success"
        self.assertEqual(classify_failure_pair(self.a, self.b), "NO_TWO_FAILURE_TRIGGER")


if __name__ == "__main__":
    unittest.main()
