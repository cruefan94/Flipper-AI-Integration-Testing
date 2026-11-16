#!/usr/bin/env python3
"""Public-safe, offline two-failure CI routing decision regression tests.

Only synthetic GitHub run metadata; never include private logs or artifacts.
Run: python3 -m unittest discover -s tests -p 'test_two_failure_fallback_policy.py'
"""
import unittest


def decision(runs, private_actions_read=True):
    """Runs ordered newest-first, restricted to ONE workflow and branch.

    A run: {id, status, conclusion, jobs_provisioned}. Never include logs.
    """
    if not private_actions_read:
        return "BLOCKED_ACTIONS_READ_403"
    if len(runs) < 2:
        return "WAIT_FOR_EVIDENCE"
    latest, previous = runs[:2]
    if any(r.get("status") != "completed" for r in (latest, previous)):
        return "WAIT_FOR_EVIDENCE"
    failing = {"failure", "timed_out", "cancelled", "startup_failure"}
    if all(r.get("conclusion") in failing for r in (latest, previous)):
        return "PUBLIC_SAFE_FALLBACK_REQUIRED"
    if all(r.get("conclusion") in failing and r.get("jobs_provisioned") is False
           for r in (latest, previous)):
        return "PUBLIC_SAFE_FALLBACK_REQUIRED"
    return "NO_FALLBACK"


class PolicyTests(unittest.TestCase):
    def test_two_failures(self):
        self.assertEqual(decision([
            dict(id=102, status="completed", conclusion="failure", jobs_provisioned=True),
            dict(id=101, status="completed", conclusion="failure", jobs_provisioned=True),
        ]), "PUBLIC_SAFE_FALLBACK_REQUIRED")

    def test_repeated_no_runner(self):
        self.assertEqual(decision([
            dict(id=102, status="completed", conclusion="startup_failure", jobs_provisioned=False),
            dict(id=101, status="completed", conclusion="startup_failure", jobs_provisioned=False),
        ]), "PUBLIC_SAFE_FALLBACK_REQUIRED")

    def test_single_failure(self):
        self.assertEqual(decision([
            dict(id=102, status="completed", conclusion="failure", jobs_provisioned=True),
            dict(id=101, status="completed", conclusion="success", jobs_provisioned=True),
        ]), "NO_FALLBACK")

    def test_pending_not_counted(self):
        self.assertEqual(decision([
            dict(id=102, status="in_progress", conclusion=None, jobs_provisioned=True),
            dict(id=101, status="completed", conclusion="failure", jobs_provisioned=True),
        ]), "WAIT_FOR_EVIDENCE")

    def test_permission_denied(self):
        self.assertEqual(decision([], private_actions_read=False), "BLOCKED_ACTIONS_READ_403")

    def test_no_evidence(self):
        self.assertEqual(decision([]), "WAIT_FOR_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
