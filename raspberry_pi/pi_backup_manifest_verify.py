"""Read-only integrity verification for *existing* Pi/qFlipper backup files.

Manifest format: {"files": [{"path": "subdir/name.bin", "size": 123,
                              "sha256": "<64 lowercase hex>"}]}
No device I/O, backup creation, restoration, or filesystem writes.
"""
from __future__ import annotations

import hashlib
import json
import re
import stat
from pathlib import Path, PurePosixPath

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_CHUNK = 1024 * 1024


def _safe_path(root: Path, name: object) -> Path | None:
    if not isinstance(name, str) or not name or "\\" in name:
        return None
    pure = PurePosixPath(name)
    if pure.is_absolute() or any(p in ("", ".", "..") for p in name.split("/")):
        return None
    current = root
    for component in pure.parts:
        current = current / component
        try:
            mode = current.lstat().st_mode
        except OSError:
            return None
        if stat.S_ISLNK(mode):
            return None
    return current


def verify_manifest(backup_root: Path, manifest: dict) -> dict:
    """Validate listed files without opening any serial device or changing data."""
    root = Path(backup_root)
    try:
        if not stat.S_ISDIR(root.lstat().st_mode) or root.is_symlink():
            return {"ok": False, "results": [{"status": "invalid_root"}]}
    except OSError:
        return {"ok": False, "results": [{"status": "invalid_root"}]}
    entries = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(entries, list):
        return {"ok": False, "results": [{"status": "invalid_manifest"}]}
    results = []
    seen = set()
    for entry in entries:
        name = entry.get("path") if isinstance(entry, dict) else None
        size = entry.get("size") if isinstance(entry, dict) else None
        digest = entry.get("sha256") if isinstance(entry, dict) else None
        if (not isinstance(name, str) or name in seen
                or type(size) is not int or size < 0
                or not isinstance(digest, str) or not _DIGEST.fullmatch(digest)):
            results.append({"status": "invalid_entry"})
            continue
        seen.add(name)
        path = _safe_path(root, name)
        if path is None:
            results.append({"status": "unsafe_or_missing_path"})
            continue
        try:
            if not stat.S_ISREG(path.lstat().st_mode):
                results.append({"status": "not_regular_file"})
                continue
            actual = hashlib.sha256()
            total = 0
            with path.open("rb") as stream:
                while chunk := stream.read(_CHUNK):
                    total += len(chunk)
                    actual.update(chunk)
            status = "ok" if total == size and actual.hexdigest() == digest else "mismatch"
        except OSError:
            status = "read_error"
        results.append({"status": status})
    return {"ok": all(r["status"] == "ok" for r in results), "results": results,
            "read_only": True, "identity_verified": False}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Verify an existing backup; never restore")
    parser.add_argument("backup_root", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        with args.manifest.open(encoding="utf-8") as stream:
            data = json.load(stream)
        result = verify_manifest(args.backup_root, data)
    except (OSError, ValueError):
        result = {"ok": False, "results": [{"status": "invalid_manifest"}]}
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
