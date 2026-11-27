#!/usr/bin/env python3
"""Create and verify public-safe SHA256 evidence for locally built artifacts.

This tool does NOT sign, release, publish, install, decrypt, or certify a
physical-device test. It stores no credential or private source content.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

REPOSITORIES = {
    "cruefan94/Flipper-AI-Momentum-",
    "cruefan94/Flipper-AI-Android-Satellite",
    "cruefan94/Flipper-AI-Integration-Testing",
}
KINDS = {"android-apk", "momentum-f7", "esp32", "integration-fixture"}
SHA_PATTERN = re.compile(r"[a-f0-9]{40}\Z")
DIGEST_PATTERN = re.compile(r"[a-f0-9]{64}\Z")
MAX_FILES = 100


class EvidenceError(ValueError):
    """Fail closed on incomplete, ambiguous, or unsafe evidence."""


def safe_path(root: Path, entry: str) -> Path:
    if not isinstance(entry, str) or not entry or "\\" in entry:
        raise EvidenceError("Unsafe or empty relative artifact path")
    relative = PurePosixPath(entry)
    if (relative.is_absolute() or entry != relative.as_posix()
            or any(part in ("", ".", "..") for part in entry.split("/"))
            or ":" in entry):
        raise EvidenceError("Artifact path must be clean and relative")
    target = root / entry
    if target.resolve() != target or not target.is_file() or target.is_symlink():
        raise EvidenceError("Missing artifact, symlink, or path escape")
    return target


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_header(evidence: dict) -> None:
    if not isinstance(evidence, dict) or set(evidence) != {
        "schema", "repository", "source_sha", "kind", "scope", "artifacts"
    }:
        raise EvidenceError("Unknown or incomplete evidence schema")
    if evidence["schema"] != 1 or evidence["repository"] not in REPOSITORIES:
        raise EvidenceError("Unsupported schema or source repository")
    if not isinstance(evidence["source_sha"], str) or not SHA_PATTERN.fullmatch(evidence["source_sha"]):
        raise EvidenceError("Full lowercase 40-digit source SHA required")
    if evidence["kind"] not in KINDS or evidence["scope"] != "build-artifact-only":
        raise EvidenceError("Unsupported kind or false verification scope")


def write(root: Path, output: Path, repository: str, source_sha: str,
          kind: str, names: list[str]) -> None:
    root = root.resolve(strict=True)
    if not root.is_dir() or not 1 <= len(names) <= MAX_FILES or len(names) != len(set(names)):
        raise EvidenceError("Expected 1-100 unique artifact files under a directory")
    evidence = {
        "schema": 1, "repository": repository, "source_sha": source_sha,
        "kind": kind, "scope": "build-artifact-only", "artifacts": []
    }
    check_header(evidence)
    for name in sorted(names):
        file = safe_path(root, name)
        if file.resolve() == output.resolve():
            raise EvidenceError("Manifest must not hash itself")
        evidence["artifacts"].append({
            "path": name, "bytes": file.stat().st_size,
            "sha256": sha256_file(file),
        })
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify(root: Path, manifest: Path, expected_sha: str | None = None) -> dict:
    root = root.resolve(strict=True)
    evidence = json.loads(manifest.read_text(encoding="utf-8"))
    check_header(evidence)
    if expected_sha is not None and expected_sha != evidence["source_sha"]:
        raise EvidenceError("Manifest source SHA does not match selected build")
    artifacts = evidence["artifacts"]
    if not isinstance(artifacts, list) or not 1 <= len(artifacts) <= MAX_FILES:
        raise EvidenceError("Missing or excessive artifact inventory")
    seen = set()
    for record in artifacts:
        if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
            raise EvidenceError("Invalid artifact record")
        name = record["path"]
        if not isinstance(name, str) or name in seen:
            raise EvidenceError("Duplicate artifact path")
        seen.add(name)
        file = safe_path(root, name)
        if (type(record["bytes"]) is not int or record["bytes"] < 0
                or record["bytes"] != file.stat().st_size
                or not isinstance(record["sha256"], str)
                or not DIGEST_PATTERN.fullmatch(record["sha256"])
                or record["sha256"] != sha256_file(file)):
            raise EvidenceError("Artifact size or digest mismatch")
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    pack = subs.add_parser("write")
    pack.add_argument("--root", type=Path, required=True)
    pack.add_argument("--output", type=Path, required=True)
    pack.add_argument("--repository", choices=sorted(REPOSITORIES), required=True)
    pack.add_argument("--source-sha", required=True)
    pack.add_argument("--kind", choices=sorted(KINDS), required=True)
    pack.add_argument("files", nargs="+", help="Relative artifact paths below --root")
    check = subs.add_parser("verify")
    check.add_argument("--root", type=Path, required=True)
    check.add_argument("--manifest", type=Path, required=True)
    check.add_argument("--expected-sha")
    args = parser.parse_args()
    try:
        if args.command == "write":
            write(args.root, args.output, args.repository, args.source_sha, args.kind, args.files)
            print("Manifest generated: build artifacts only; NOT hardware tested")
        else:
            evidence = verify(args.root, args.manifest, args.expected_sha)
            print(f"Verified {len(evidence['artifacts'])} artifacts: build evidence only; NOT hardware tested")
    except (EvidenceError, OSError, ValueError, json.JSONDecodeError) as error:
        parser.exit(1, f"Evidence verification failed: {error}\n")


if __name__ == "__main__":
    main()
