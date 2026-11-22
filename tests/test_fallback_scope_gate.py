"""Public-safe offline gate: a green fallback is not native firmware proof.

Consumes manually sanitized job conclusions only; no GitHub API or private data.
"""
import unittest


REQUIRED_NATIVE = frozenset({"firmware", "contract", "protocol"})


def classify_fallback(run_conclusion, jobs):
    """Return (admissible, reason); never infer artifact integrity from a green run."""
    if run_conclusion != "success":
        return False, "fallback workflow not successful"
    if not isinstance(jobs, dict):
        return False, "job evidence missing"
    for name in REQUIRED_NATIVE:
        if jobs.get(name) != "success":
            return False, "native evidence incomplete"
    # Passing native jobs alone is not proof of DFU suffix CRC or artifact hashes.
    return False, "exact-artifact CRC and SHA-256 attestation required"


class FallbackScopeTests(unittest.TestCase):
    def test_green_diagnostic_only_rejected(self):
        ok, reason = classify_fallback("success", {
            "describe": "success", "diagnostic": "success",
            "firmware": "skipped", "contract": "skipped", "protocol": "skipped"})
        self.assertFalse(ok)
        self.assertEqual(reason, "native evidence incomplete")

    def test_failed_workflow_rejected(self):
        self.assertFalse(classify_fallback("failure", {"firmware": "success"})[0])

    def test_missing_job_evidence_rejected(self):
        self.assertFalse(classify_fallback("success", None)[0])

    def test_native_success_still_requires_artifact_proof(self):
        ok, reason = classify_fallback("success", {
            "firmware": "success", "contract": "success", "protocol": "success"})
        self.assertFalse(ok)
        self.assertIn("CRC", reason)

    def test_skipped_protocol_rejected(self):
        self.assertEqual(classify_fallback("success", {
            "firmware": "success", "contract": "success", "protocol": "skipped"})[1],
            "native evidence incomplete")


if __name__ == "__main__":
    unittest.main()
