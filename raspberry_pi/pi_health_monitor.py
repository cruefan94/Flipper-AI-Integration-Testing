"""Read-only Raspberry Pi OS health snapshots, with no device identifiers or writes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import time

def read_text(path: Path) -> str | None:
    try:
        with path.open("r", encoding="utf-8") as stream:
            return stream.read(4096)
    except (OSError, UnicodeError):
        return None

def parse_meminfo(text: str | None) -> dict:
    fields = {}
    for line in (text or "").splitlines():
        key, sep, value = line.partition(":")
        if sep and key in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree"):
            parts = value.strip().split()
            if len(parts) == 2 and parts[1] == "kB" and parts[0].isdigit():
                fields[key] = int(parts[0])
    return {name: fields.get(key, 0) // 1024 for name, key in (
        ("total_mib", "MemTotal"), ("available_mib", "MemAvailable"),
        ("swap_total_mib", "SwapTotal"), ("swap_free_mib", "SwapFree"))}

def parse_temperature(text: str | None) -> float | None:
    try:
        value = int((text or "").strip()) / 1000
        return round(value, 1) if -20 <= value <= 125 else None
    except ValueError:
        return None

def snapshot(root: Path = Path("/")) -> dict:
    proc = root / "proc"
    uptime = read_text(proc / "uptime")
    try:
        seconds = int(float(uptime.split()[0])) if uptime else None
    except (ValueError, IndexError):
        seconds = None
    pressure = read_text(proc / "pressure/memory")
    pressure_avg10 = None
    for line in (pressure or "").splitlines():
        if line.startswith("some "):
            for part in line.split():
                if part.startswith("avg10="):
                    try:
                        pressure_avg10 = float(part.split("=", 1)[1])
                    except ValueError:
                        pass
    return {
        "cpu_temp_c": parse_temperature(read_text(root / "sys/class/thermal/thermal_zone0/temp")),
        "memory": parse_meminfo(read_text(proc / "meminfo")),
        "uptime_seconds": seconds,
        "memory_pressure_some_avg10": pressure_avg10,
        "note": "Read-only Pi OS snapshot; no OLED, Flipper or ESP32 device access",
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.interval < 10:
        parser.error("interval must be at least 10 seconds")
    while True:
        print(json.dumps(snapshot(), sort_keys=True), flush=True)
        if args.once:
            break
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
