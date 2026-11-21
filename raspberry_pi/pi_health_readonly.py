"""Read-only Pi OS health snapshots; no Pironman hardware control.

Reads kernel-provided metrics only. No sudo, GPIO, I2C, USB or network calls.
Run with --once for a single snapshot, or --watch --consent for 10s intervals.
"""
import argparse
import json
import math
from pathlib import Path
import time

def parse_meminfo(text):
    values = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        name, raw = line.split(":", 1)
        fields = raw.strip().split()
        if name in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree") and fields:
            if len(fields) != 2 or fields[1] != "kB":
                raise ValueError("unexpected memory units")
            values[name] = int(fields[0]) * 1024
            if values[name] < 0:
                raise ValueError("negative memory metric")
    if not {"MemTotal", "MemAvailable"}.issubset(values):
        raise ValueError("missing memory metrics")
    if values["MemAvailable"] > values["MemTotal"]:
        raise ValueError("available memory exceeds total")
    return values

def snapshot(proc=Path("/proc"), thermal=Path("/sys/class/thermal/thermal_zone0/temp")):
    memory = parse_meminfo((proc / "meminfo").read_text(encoding="ascii"))
    load = (proc / "loadavg").read_text(encoding="ascii").split()[:3]
    if len(load) != 3:
        raise ValueError("missing load averages")
    load_values = [float(x) for x in load]
    if any(not math.isfinite(x) or x < 0 for x in load_values):
        raise ValueError("invalid load average")
    result = {"status": "read_only", "memory_bytes": memory,
              "load_averages": load_values,
              "temperature_c": None, "hardware_control": False}
    try:
        result["temperature_c"] = round(int(thermal.read_text(encoding="ascii").strip()) / 1000, 1)
    except (OSError, ValueError):
        pass
    return result

def main():
    parser = argparse.ArgumentParser(description="Read-only Raspberry Pi health monitor")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true")
    mode.add_argument("--watch", action="store_true")
    parser.add_argument("--consent", action="store_true", help="Required for continuous sampling")
    args = parser.parse_args()
    if args.watch and not args.consent:
        parser.error("--watch requires --consent")
    while True:
        print(json.dumps(snapshot(), sort_keys=True), flush=True)
        if args.once:
            break
        time.sleep(10)

if __name__ == "__main__":
    main()
