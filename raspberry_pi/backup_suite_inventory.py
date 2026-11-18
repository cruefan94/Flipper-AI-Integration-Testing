"""Read-only, public-safe Pi backup suite inventory gate.

Presence is not execution. No hardware, backups, network, secrets, or
privileged operations are accessed. Symlinks never satisfy the gate.
"""
from pathlib import Path
import stat
import sys

REQUIRED_SUITES = {
    "manifest_verifier": "test_pi_backup_manifest_verify.py",
    "readiness_contract": "test_pi_backup_readiness_contract.py",
    "privacy_contract": "test_pi_readiness_privacy_contract.py",
}


def inspect_suite_presence(root: Path) -> dict[str, bool]:
    """Return fixed labels only, rejecting symlink roots and suite files."""
    try:
        root_ok = stat.S_ISDIR(root.lstat().st_mode)
    except OSError:
        root_ok = False

    def regular_file(filename: str) -> bool:
        if not root_ok:
            return False
        try:
            return stat.S_ISREG((root / filename).lstat().st_mode)
        except OSError:
            return False

    return {label: regular_file(filename)
            for label, filename in REQUIRED_SUITES.items()}


def main() -> int:
    root = Path(__file__).resolve().parent / "tests"
    inventory = inspect_suite_presence(root)
    for label, present in inventory.items():
        print(f"{label}: {'PRESENT' if present else 'MISSING'}")
    if not all(inventory.values()):
        print("BLOCKED: required suite files absent or unsafe; no candidate promotion")
        return 1
    print("PRESENCE ONLY: execution, counts and CI remain unverified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
