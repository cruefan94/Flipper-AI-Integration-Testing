"""Offline regression checks for public-safe fallback evidence admission."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "fallback", Path(__file__).resolve().parents[1] / "scripts" / "validate_fallback_evidence.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def sample():
    return {
        "failures": [
            {"run_id": 101, "workflow": "native-protocol", "branch": "review", "status": "completed", "conclusion": "failure"},
            {"run_id": 102, "workflow": "native-protocol", "branch": "review", "status": "completed", "conclusion": "failure"},
        ],
        "fallback": {"state": "BLOCKED", "reason": "Actions dispatch permission unavailable"},
        "release_ready": False,
    }


class FallbackEvidenceTests(unittest.TestCase):
    def test_blocked_is_honest(self):
        self.assertEqual(module.validate(sample()), [])

    def test_cross_workflow_not_a_pair(self):
        data = sample()
        data["failures"][1]["workflow"] = "full-build"
        self.assertTrue(module.validate(data))

    def test_incomplete_or_duplicate_failure_rejected(self):
        data = sample()
        data["failures"][1]["run_id"] = 101
        self.assertTrue(module.validate(data))
        data["failures"][1]["status"] = "queued"
        self.assertTrue(module.validate(data))

    def test_dispatch_requires_real_run_and_url(self):
        data = sample()
        data["fallback"] = {"state": "DISPATCHED"}
        self.assertTrue(module.validate(data))
        data["fallback"]["run_id"] = 103
        data["fallback"]["url"] = "https://github.com/example/repo/actions/runs/103"
        self.assertEqual(module.validate(data), [])

    def test_completed_requires_terminal_result(self):
        data = sample()
        data["fallback"] = {"state": "COMPLETED", "run_id": 103, "url": "https://github.com/example/repo/actions/runs/103"}
        self.assertTrue(module.validate(data))
        data["fallback"]["conclusion"] = "success"
        self.assertEqual(module.validate(data), [])

    def test_fallback_never_implies_release(self):
        data = sample()
        data["release_ready"] = True
        self.assertTrue(module.validate(data))


if __name__ == "__main__":
    unittest.main()
