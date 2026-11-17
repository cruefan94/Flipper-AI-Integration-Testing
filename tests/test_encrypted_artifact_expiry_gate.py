"""Public-safe artifact metadata release gate. No downloads or private data.

Usage: python3 -m unittest tests/test_encrypted_artifact_expiry_gate.py -v
This checks GitHub artifact metadata only, not native DFU CRC or firmware safety.
"""
import datetime as dt
import re
import unittest

UTC = dt.timezone.utc
HEX64 = re.compile(r"^sha256:[0-9a-f]{64}$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_REPO = "cruefan94/Flipper-AI-Integration-Testing"


def validate_encrypted_artifact(metadata, now):
    """Fail closed for release evidence; never infer flash approval."""
    if not isinstance(now, dt.datetime) or now.tzinfo is None:
        raise ValueError("timezone-aware now required")
    required = {"id", "name", "expired", "expires_at", "digest",
                "workflow_run", "size_in_bytes"}
    if not isinstance(metadata, dict) or not required.issubset(metadata):
        raise ValueError("incomplete artifact metadata")
    if type(metadata["id"]) is not int or metadata["id"] <= 0:
        raise ValueError("invalid artifact ID")
    if type(metadata["size_in_bytes"]) is not int or metadata["size_in_bytes"] <= 0:
        raise ValueError("invalid artifact size")
    if not isinstance(metadata["name"], str) or not metadata["name"].startswith("encrypted-"):
        raise ValueError("artifact not identified as encrypted")
    if metadata["expired"] is not False:
        raise ValueError("artifact expired or status unknown")
    if not isinstance(metadata["digest"], str) or not HEX64.fullmatch(metadata["digest"]):
        raise ValueError("invalid encrypted ZIP digest")
    try:
        expiry = dt.datetime.fromisoformat(metadata["expires_at"].replace("Z", "+00:00"))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError("invalid expiry") from exc
    if expiry.tzinfo is None or now >= expiry:
        raise ValueError("artifact no longer available")
    run = metadata["workflow_run"]
    if not isinstance(run, dict) or type(run.get("id")) is not int or run["id"] <= 0:
        raise ValueError("missing workflow run identity")
    if not isinstance(run.get("head_sha"), str) or not SHA40.fullmatch(run["head_sha"]):
        raise ValueError("missing exact commit SHA")
    return {"artifact_id": metadata["id"], "workflow_run_id": run["id"],
            "head_sha": run["head_sha"], "encrypted_zip_sha256": metadata["digest"][7:],
            "expires_at": expiry.isoformat(), "native_dfu_crc_verified": False,
            "native_tgz_hash_verified": False, "flash_approved": False}


class ArtifactExpiryTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime(2026, 11, 16, 21, 0, tzinfo=UTC)
        self.record = {"id": 123, "name": "encrypted-example-UNTESTED",
                       "expired": False, "expires_at": "2026-11-23T08:15:58Z",
                       "digest": "sha256:" + "a" * 64, "size_in_bytes": 100,
                       "workflow_run": {"id": 456, "head_sha": "b" * 40}}

    def test_valid_metadata_still_holds_flash(self):
        evidence = validate_encrypted_artifact(self.record, self.now)
        self.assertFalse(evidence["flash_approved"])
        self.assertFalse(evidence["native_dfu_crc_verified"])
        self.assertFalse(evidence["native_tgz_hash_verified"])

    def test_expired_flag_rejected(self):
        self.record["expired"] = True
        with self.assertRaises(ValueError):
            validate_encrypted_artifact(self.record, self.now)

    def test_elapsed_expiry_rejected(self):
        self.record["expires_at"] = "2026-11-15T08:15:58Z"
        with self.assertRaises(ValueError):
            validate_encrypted_artifact(self.record, self.now)

    def test_exact_expiry_boundary_rejected(self):
        self.record["expires_at"] = "2026-11-16T21:00:00Z"
        with self.assertRaises(ValueError):
            validate_encrypted_artifact(self.record, self.now)

    def test_unencrypted_name_rejected(self):
        self.record["name"] = "native-firmware.tgz"
        with self.assertRaises(ValueError):
            validate_encrypted_artifact(self.record, self.now)

    def test_wrong_digest_rejected(self):
        self.record["digest"] = "sha256:example"
        with self.assertRaises(ValueError):
            validate_encrypted_artifact(self.record, self.now)

    def test_missing_commit_rejected(self):
        self.record["workflow_run"].pop("head_sha")
        with self.assertRaises(ValueError):
            validate_encrypted_artifact(self.record, self.now)

    def test_naive_clock_rejected(self):
        with self.assertRaises(ValueError):
            validate_encrypted_artifact(self.record, dt.datetime(2026, 11, 16))

    def test_boolean_size_rejected(self):
        self.record["size_in_bytes"] = True
        with self.assertRaises(ValueError):
            validate_encrypted_artifact(self.record, self.now)


if __name__ == "__main__":
    unittest.main()
