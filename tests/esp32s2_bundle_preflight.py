#!/usr/bin/env python3
"""Public, standalone ESP32-S2 bundle preflight. No private firmware sources."""
import hashlib
import json
import sys
from pathlib import Path

def verify(path):
    path = Path(path).resolve()
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("chip") != "esp32s2":
        raise ValueError("chip must be esp32s2")
    entries = doc.get("images")
    if not isinstance(entries, list) or not entries:
        raise ValueError("images missing")
    ranges = []
    for item in entries:
        rel = item["file"]
        file = (path.parent / rel).resolve()
        if not file.is_relative_to(path.parent) or not file.is_file():
            raise ValueError("unsafe or missing image")
        off = int(item["offset"], 0)
        if off < 0 or off % 4096:
            raise ValueError("invalid offset")
        payload = file.read_bytes()
        if not payload or hashlib.sha256(payload).hexdigest() != item["sha256"].lower():
            raise ValueError("invalid checksum")
        if off + len(payload) > 0x400000:
            raise ValueError("outside conservative 4 MB boundary")
        ranges.append((off, off + len(payload)))
    ranges.sort()
    if any(left[1] > right[0] for left, right in zip(ranges, ranges[1:])):
        raise ValueError("overlapping flash regions")
    return len(entries)

if __name__ == "__main__":
    try:
        print("PASS:", verify(sys.argv[1]), "images")
    except (IndexError, ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        sys.exit("FAIL: " + str(exc))
