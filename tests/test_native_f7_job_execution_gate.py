#!/usr/bin/env python3
"""Fail-closed public-safe GitHub Actions job-execution gate.

Consumes sanitized GitHub Actions jobs JSON ({"jobs": [...]}) produced by an
authorized PRIVATE reader. Never upload private job logs, firmware or tokens.
This only checks execution metadata; it cannot prove artifact integrity.
"""
import argparse
import json
import sys
import unittest

REQUIRED = (
    "Full F7 AI1 firmware compile and strict update inspection",
    "Private DRAFT release with direct native TGZ download (no decryption)",
)


def evaluate(payload, required=REQUIRED):
    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        return False, "missing jobs array"
    jobs = payload["jobs"]
    if any(not isinstance(job, dict) for job in jobs):
        return False, "invalid job entry"
    for name in required:
        matches = [job for job in jobs if job.get("name") == name]
        if len(matches) != 1:
            return False, "missing or ambiguous required job: " + name
        job = matches[0]
        if job.get("status") != "completed" or job.get("conclusion") != "success":
            return False, "required job not executed successfully: " + name
    return True, "required jobs executed successfully (artifact checks still required)"


class ExecutionGateTests(unittest.TestCase):
    def fixture(self, first="success", second="success"):
        return {"jobs": [
            {"name": REQUIRED[0], "status": "completed", "conclusion": first},
            {"name": REQUIRED[1], "status": "completed", "conclusion": second},
        ]}

    def test_two_successes(self):
        self.assertTrue(evaluate(self.fixture())[0])

    def test_skipped_native(self):
        self.assertFalse(evaluate(self.fixture("skipped"))[0])

    def test_skipped_package(self):
        self.assertFalse(evaluate(self.fixture(second="skipped"))[0])

    def test_failure(self):
        self.assertFalse(evaluate(self.fixture("failure"))[0])

    def test_queued(self):
        p = self.fixture()
        p["jobs"][0]["status"] = "queued"
        self.assertFalse(evaluate(p)[0])

    def test_duplicate_name(self):
        p = self.fixture()
        p["jobs"].append(p["jobs"][0].copy())
        self.assertFalse(evaluate(p)[0])

    def test_missing_job(self):
        self.assertFalse(evaluate({"jobs": []})[0])

    def test_malformed(self):
        self.assertFalse(evaluate({"jobs": ["bad"]})[0])

    def test_green_quick_check_only(self):
        self.assertFalse(evaluate({"jobs": [
            {"name": "Private quick source checks (no duplicate full compile)",
             "status": "completed", "conclusion": "success"}
        ]})[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs-json", help="Path to sanitized Actions jobs JSON")
    args = parser.parse_args()
    if not args.jobs_json:
        unittest.main(argv=[sys.argv[0]])
    else:
        try:
            with open(args.jobs_json, encoding="utf-8") as handle:
                payload = json.load(handle)
            ok, reason = evaluate(payload)
        except (OSError, ValueError) as exc:
            ok, reason = False, "invalid input: " + type(exc).__name__
        print(("PASS: " if ok else "BLOCKED: ") + reason)
        sys.exit(0 if ok else 1)
