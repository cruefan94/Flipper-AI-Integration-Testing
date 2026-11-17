"""Privacy-preserving, read-only summary of an existing backup verification result.

This module never opens files or devices and never authorizes restoration.
"""
from __future__ import annotations

_ALLOWED = frozenset({
    "ok", "mismatch", "invalid_entry", "unsafe_or_missing_path",
    "not_regular_file", "read_error", "invalid_root", "invalid_manifest",
})


def summarize_readiness(verification: object) -> dict:
    """Return aggregate counts only, never paths, hashes or source metadata."""
    invalid = {
        "ready_for_manual_review": False,
        "verified_files": 0,
        "total_files": 0,
        "failed_files": 0,
        "identity_verified": False,
        "restore_authorized": False,
        "status": "invalid_verification",
    }
    if not isinstance(verification, dict):
        return invalid
    results = verification.get("results")
    if not isinstance(results, list) or not results:
        return invalid
    statuses = []
    for item in results:
        if not isinstance(item, dict):
            return invalid
        status = item.get("status")
        if not isinstance(status, str) or status not in _ALLOWED:
            return invalid
        statuses.append(status)
    passed = statuses.count("ok")
    consistent = (
        verification.get("ok") is True
        and verification.get("read_only") is True
        and verification.get("identity_verified") is False
        and passed == len(statuses)
    )
    return {
        "ready_for_manual_review": consistent,
        "verified_files": passed,
        "total_files": len(statuses),
        "failed_files": len(statuses) - passed,
        "identity_verified": False,
        "restore_authorized": False,
        "status": "integrity_checked" if consistent else "needs_attention",
    }
