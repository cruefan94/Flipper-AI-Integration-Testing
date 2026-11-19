"""Offline, read-only evaluation of owner-supplied qFlipper backup evidence.

No file reads, hashes, serial ports, hardware commands, or flashing.
An inventory report is never treated as evidence of a restorable backup.
"""
from __future__ import annotations

from typing import Any, Mapping


def assess_backup_evidence(evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Require independent owner-observed backup and restore evidence.

    This is an advisory checklist, not an authorization to perform recovery.
    All fields must be literal booleans; strings and inferred port presence fail.
    """
    required = (
        "owner_confirmed_backup_exists",
        "owner_confirmed_backup_hash_matches",
        "owner_confirmed_backup_stored_separately",
        "owner_confirmed_restore_procedure_reviewed",
    )
    checks = {key: evidence.get(key) is True for key in required}
    complete = all(checks.values())
    return {
        "schema_version": 1,
        "checks": checks,
        "evidence_complete": complete,
        "backup_restored_on_device": False,
        "hardware_verified": False,
        "safe_to_flash": False,
        "next_step": (
            "Owner must independently verify backup contents and recovery on their own device; "
            "this report does not authorize flashing."
        ),
    }
