"""Read-only, public-safe Pi backup suite inventory gate.

This checks test *presence*, not passing execution. No hardware, backups, network,
secrets or privileged operations are accessed.
"""
from pathlib import Path
import sys

REQUIRED_SUITES = {
    "manifest_verifier": "test_pi_backup_manifest_verify.py",
    "readiness_contract": "test_pi_backup_readiness_contract.py",
    "privacy_contract": "test_pi_readiness_privacy_contract.py",
}


def inspect_suite_presence(root: Path) -> dict[str, bool]:
    """Return fixed labels only; never expose filesystem paths."""
    return {label: (root / filename).is_file()
            for label, filename in REQUIRED_SUITES.items()}


def main() -> int:
    root = Path(__file__).resolve().parent / "tests"
    inventory = inspect_suite_presence(root)
    for label, present in inventory.items():
        print(f"{label}: {'PRESENT' if present else 'MISSING'}")
    if not all(inventory.values()):
        print("BLOCKED: required suite files absent; no candidate promotion")
        return 1
    print("PRESENCE ONLY: execution, counts and CI remain unverified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
