#!/usr/bin/env python3
"""Read-only qFlipper progress observer for the Raspberry Pi AI companion.

This does not start, control, or flash a device. qFlipper's GUI progress is
not exposed through a stable public API; only explicit log percentages count.
"""
import argparse
import json
import re
import time
from pathlib import Path

# Require explicit firmware-update context to avoid confusing unrelated %.
UPDATE = re.compile(r"\b(?:firmware|update|updater|flashing|flash)\b", re.I)
PERCENT = re.compile(r"(?<!\d)(100|[1-9]?\d)\s*%(?!\d)")
SUCCESS = re.compile(r"\b(?:update|firmware|flashing)\b.{0,90}\b(?:completed|successful|finished)\b", re.I)
FAILURE = re.compile(r"\b(?:update|firmware|flashing)\b.{0,90}\b(?:failed|error|aborted)\b", re.I)

def parse_line(line):
    """Return only evidence explicitly present in a qFlipper log line."""
    if not UPDATE.search(line):
        return None
    if FAILURE.search(line):
        return {"status": "failed", "percent": None, "evidence": line.strip()[:240]}
    if SUCCESS.search(line):
        return {"status": "reported_complete", "percent": None, "evidence": line.strip()[:240]}
    match = PERCENT.search(line)
    if match:
        return {"status": "reported_progress", "percent": int(match.group(1)), "evidence": line.strip()[:240]}
    return None

def observe(path, follow=False, interval=1.0):
    """Yield evidence from an owner-selected local log; never infer missing %."""
    file = Path(path).expanduser()
    with file.open("r", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            result = parse_line(line)
            if result:
                yield result
        while follow:
            line = stream.readline()
            if line:
                result = parse_line(line)
                if result:
                    yield result
            else:
                time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description="Read-only qFlipper log progress observer")
    parser.add_argument("--log", required=True, help="Existing qFlipper log file to read")
    parser.add_argument("--follow", action="store_true", help="Watch appended log lines")
    args = parser.parse_args()
    path = Path(args.log).expanduser()
    if not path.is_file():
        parser.error("Log file not found; progress unavailable. Select a real qFlipper log.")
    print(json.dumps({"status": "monitoring", "percent": None,
                      "note": "Only explicit firmware-update percentages in this log are reported."}), flush=True)
    try:
        for item in observe(path, args.follow):
            print(json.dumps(item), flush=True)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
