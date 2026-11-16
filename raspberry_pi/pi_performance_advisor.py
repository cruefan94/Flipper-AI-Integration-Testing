"""Read-only Pi OS performance hints. Never kills processes or clears caches."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pi_health_monitor import read_text


def parse_loadavg(raw: str | None) -> tuple[float, float, float] | None:
    try:
        fields = (raw or "").split()
        if len(fields) < 3:
            return None
        values = tuple(float(x) for x in fields[:3])
        if any(not (0 <= x < 100000) for x in values):
            return None
        return values
    except (ValueError, OverflowError):
        return None


def parse_cpu_totals(raw: str | None) -> dict[str, int] | None:
    """Cumulative counters only; not an instantaneous CPU percentage."""
    fields = (raw or "").splitlines()
    if not fields or not fields[0].startswith("cpu "):
        return None
    try:
        numbers = [int(v) for v in fields[0].split()[1:]]
    except ValueError:
        return None
    if len(numbers) < 4 or any(n < 0 for n in numbers):
        return None
    return {"total_ticks": sum(numbers), "idle_ticks": numbers[3] + (numbers[4] if len(numbers) > 4 else 0)}


def parse_mem_kib(raw: str | None) -> dict[str, int | None]:
    wanted = ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree", "Cached")
    values: dict[str, int | None] = {key: None for key in wanted}
    for line in (raw or "").splitlines():
        key, separator, rest = line.partition(":")
        if separator and key in values:
            parts = rest.split()
            if len(parts) == 2 and parts[0].isascii() and parts[0].isdigit() and parts[1] == "kB":
                values[key] = int(parts[0])
    return values


def snapshot(root: Path = Path("/")) -> dict:
    proc = root / "proc"
    mem = parse_mem_kib(read_text(proc / "meminfo"))
    available = mem["MemAvailable"]
    total = mem["MemTotal"]
    swap_free = mem["SwapFree"]
    swap_total = mem["SwapTotal"]
    hints = []
    if total and available is not None and 0 <= available <= total and available * 100 < total * 15:
        hints.append("Low available RAM: close unused browser tabs before opening more apps.")
    if swap_total and swap_free is not None and 0 <= swap_free <= swap_total and swap_free * 100 < swap_total * 20:
        hints.append("Swap space is low: review active apps; no cleanup performed.")
    return {
        "load_average_1_5_15": parse_loadavg(read_text(proc / "loadavg")),
        "cpu_cumulative": parse_cpu_totals(read_text(proc / "stat")),
        "memory_kib": mem,
        "advice": hints,
        "read_only": True,
        "note": "Cumulative CPU counters are not utilization; no process, cache, or fan changes.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("/"), help="Read-only fixture root or system root")
    args = parser.parse_args()
    print(json.dumps(snapshot(args.root), sort_keys=True))


if __name__ == "__main__":
    main()
