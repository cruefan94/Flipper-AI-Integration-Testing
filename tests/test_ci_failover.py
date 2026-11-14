#!/usr/bin/env python3
"""Offline tests of automatic public-safe fallback detection; no GitHub network."""
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import unittest

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ci_failover", root / "scripts/ci_failover.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NOW = datetime(2026, 11, 14, 12, 0, tzinfo=timezone.utc)
FW = "cruefan94/Flipper-AI-Momentum-"
ANDROID = "cruefan94/Flipper-AI-Android-Satellite"


def run(num, when, conclusion="failure", branch="main",
        workflow_id=55, name="Flipper AI flash candidate - run from Actions",
        status="completed"):
    return {
        "id": num,
        "created_at": (NOW - timedelta(hours=when)).isoformat(),
        "conclusion": conclusion,
        "head_branch": branch,
        "head_sha": ("%040x" % num),
        "status": status,
        "workflow_id": workflow_id,
        "name": name,
        "event": "push",
    }


class FailoverPolicyTest(unittest.TestCase):
    def candidates(self, *items, repo=FW):
        return module.find_candidates(repo, list(items), NOW)

    def test_two_fails_same_branch_route_once(self):
        candidates = self.candidates(run(2, 1), run(1, 2))
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["reason"], "two_consecutive_failures")
        self.assertEqual(candidates[0]["kind"], "firmware")
        self.assertEqual(candidates[0]["run"]["id"], 2)

    def test_previous_success_resets_count(self):
        self.assertEqual(self.candidates(run(3, 1), run(2, 2, "success")), [
            {
                "repo": FW, "run": run(3, 1), "branch": "main",
                "reason": "inspect_pre_job", "kind": "firmware"
            }
        ])
        self.assertEqual(self.candidates(run(3, 1, "success"), run(2, 2)), [])

    def test_one_failure_needs_zero_jobs_in_monitor(self):
        self.assertEqual(self.candidates(run(1, 1))[0]["reason"], "inspect_pre_job")

    def test_in_progress_newer_blocks_old_failure(self):
        self.assertEqual(self.candidates(
            run(3, 1, status="in_progress", conclusion=None),
            run(2, 2), run(1, 3)), [])

    def test_different_branches_do_not_combine(self):
        items = self.candidates(run(2, 1, branch="main"), run(1, 2, branch="develop"))
        self.assertEqual(len(items), 2)
        self.assertTrue(all(i["reason"] == "inspect_pre_job" for i in items))

    def test_old_failures_do_not_route(self):
        self.assertEqual(self.candidates(run(2, 180), run(1, 181)), [])

    def test_cancelled_does_not_count(self):
        candidates = self.candidates(run(3, 1), run(2, 2, conclusion="cancelled"),
                                     run(1, 3, conclusion="failure"))
        self.assertEqual(candidates[0]["reason"], "two_consecutive_failures")

    def test_android_apk_routes_android_fallback(self):
        items = self.candidates(
            run(2, 1, name="Android Satellite — public APK build"),
            run(1, 2, name="Android Satellite — public APK build"),
            repo=ANDROID)
        self.assertEqual(items[0]["kind"], "android")

    def test_cloudflare_contract_routes_contract_fallback(self):
        items = self.candidates(
            run(2, 1, name="Cloudflare Worker contract tests"),
            run(1, 2, name="Cloudflare Worker contract tests"),
            repo=ANDROID)
        self.assertEqual(items[0]["kind"], "contract")

    def test_unmapped_private_workflow_marked_diagnostic(self):
        self.assertEqual(module.kind_for(FW, "Other extra-app build"), "diagnostic")

    def test_dedupe_uses_source_repo_and_run(self):
        candidate = self.candidates(run(2, 1), run(1, 2))[0]
        key = module.trigger_id(candidate)
        self.assertTrue(module.recorded(key, [{"display_title": "fallback | " + key}]))
        self.assertFalse(module.recorded(key + "5", [{"display_title": "fallback | " + key}]))


if __name__ == "__main__":
    unittest.main()
