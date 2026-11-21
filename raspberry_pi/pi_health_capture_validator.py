"""Offline validator for owner-redacted Pi health JSONL captures.

Never reads hardware, network, secrets, or the Pi filesystem. Input must be an
explicit local file supplied by the owner. No output includes captured values.
"""
import argparse
import json
import math
from pathlib import Path

MAX_FILE_BYTES = 65536
MAX_SAMPLES = 30

def validate_sample(sample):
    if not isinstance(sample, dict) or sample.get("status") != "read_only" or sample.get("hardware_control") is not False:
        raise ValueError("not a read-only health snapshot")
    memory = sample.get("memory_bytes")
    if not isinstance(memory, dict):
        raise ValueError("missing memory metrics")
    allowed_memory = {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}
    if set(memory) - allowed_memory:
        raise ValueError("unexpected memory fields; redact capture before validating")
    if ("SwapTotal" in memory) != ("SwapFree" in memory):
        raise ValueError("incomplete swap metrics")
    for key in ("MemTotal", "MemAvailable"):
        value = memory.get(key)
        if type(value) is not int or value < 0:
            raise ValueError("invalid memory metric")
    if memory["MemTotal"] == 0 or memory["MemAvailable"] > memory["MemTotal"]:
        raise ValueError("inconsistent memory metrics")
    for key in ("SwapTotal", "SwapFree"):
        if key in memory and (type(memory[key]) is not int or memory[key] < 0):
            raise ValueError("invalid swap metric")
    if "SwapTotal" in memory and "SwapFree" in memory and memory["SwapFree"] > memory["SwapTotal"]:
        raise ValueError("inconsistent swap metrics")
    loads = sample.get("load_averages")
    if not isinstance(loads, list) or len(loads) != 3 or any(
        type(x) not in (int, float) or not math.isfinite(x) or x < 0 for x in loads
    ):
        raise ValueError("invalid load averages")
    temp = sample.get("temperature_c")
    if temp is not None and (type(temp) not in (int, float) or not math.isfinite(temp)):
        raise ValueError("invalid temperature")
    if set(sample) != {"status", "hardware_control", "memory_bytes", "load_averages", "temperature_c"}:
        raise ValueError("unexpected fields; redact capture before validating")

def validate_text(text):
    lines = text.splitlines()
    if not 1 <= len(lines) <= MAX_SAMPLES:
        raise ValueError("expected 1 to 30 JSONL snapshots")
    for line in lines:
        validate_sample(json.loads(line))
    return len(lines)

def main():
    parser = argparse.ArgumentParser(description="Validate redacted Pi health captures offline")
    parser.add_argument("capture", type=Path, help="Owner-provided JSONL file; never uploaded")
    args = parser.parse_args()
    if not args.capture.is_file() or args.capture.stat().st_size > MAX_FILE_BYTES:
        parser.error("capture missing, not a regular file, or too large")
    try:
        count = validate_text(args.capture.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
        parser.exit(2, "INVALID: " + type(exc).__name__ + "\n")
    print(f"VALID: {count} read-only snapshot(s); no device acceptance implied")

if __name__ == "__main__":
    main()
