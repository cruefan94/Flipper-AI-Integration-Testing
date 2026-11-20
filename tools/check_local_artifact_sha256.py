#!/usr/bin/env python3
"""Offline, fail-closed SHA-256 verification for *locally supplied* candidate artifacts.

No network access, no private firmware contents or signatures in output.
This verifies bytes against a supplied digest, NOT the provenance/trustworthiness
of that digest, updater CRC, APK signer, hardware compatibility or install safety.
"""
import argparse
import hashlib
import hmac
import pathlib
import re
import sys

HEX64 = re.compile(r"[0-9a-fA-F]{64}\Z")

def verify(path: pathlib.Path, expected: str) -> bool:
    if not HEX64.fullmatch(expected):
        raise ValueError("expected SHA-256 must be exactly 64 hexadecimal characters")
    if not path.is_file() or path.is_symlink():
        raise ValueError("artifact must be an existing regular non-symlink file")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return hmac.compare_digest(digest.hexdigest(), expected.lower())

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=pathlib.Path)
    parser.add_argument("expected_sha256", help="trusted expected SHA-256 hex digest")
    args = parser.parse_args(argv)
    try:
        ok = verify(args.artifact, args.expected_sha256)
    except (ValueError, OSError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    print("PASS: artifact SHA-256 matches supplied digest" if ok else
          "FAIL: artifact SHA-256 mismatch")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
