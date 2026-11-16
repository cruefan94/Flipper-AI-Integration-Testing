"""Read-only browser memory budget hints for a 4GB Raspberry Pi.

This tool never enumerates/kills browser processes or changes OS settings.
It uses procfs memory counters, not a fabricated per-tab RAM estimate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pi_performance_advisor import parse_mem_kib
from .pi_health_monitor import read_text


def browser_budget(mem: dict[str, int | None]) -> dict:
    total = mem.get("MemTotal")
    available = mem.get("MemAvailable")
    result = {
        "status": "unavailable",
        "available_mib": None,
        "total_mib": None,
        "recommendations": ["Memory readings unavailable; no changes performed."],
        "read_only": True,
    }
    if (not isinstance(total, int) or isinstance(total, bool) or total <= 0
            or not isinstance(available, int) or isinstance(available, bool)
            or available < 0 or available > total):
        return result
    percent = available * 100 / total
    result["available_mib"] = available // 1024
    result["total_mib"] = total // 1024
    if percent < 10:
        result["status"] = "critical"
        result["recommendations"] = [
            "Very little available RAM: save browser work and close unused tabs manually.",
            "Avoid opening additional browser profiles or heavy web apps.",
        ]
    elif percent < 25:
        result["status"] = "constrained"
        result["recommendations"] = [
            "Available RAM is limited: consider reducing active browser tabs.",
        ]
    else:
        result["status"] = "comfortable"
        result["recommendations"] = [
            "No immediate memory-pressure browser action suggested.",
        ]
    return result


def snapshot(root: Path = Path("/")) -> dict:
    return browser_budget(parse_mem_kib(read_text(root / "proc" / "meminfo")))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("/"),
                        help="Read-only system or synthetic fixture root")
    args = parser.parse_args()
    print(json.dumps(snapshot(args.root), sort_keys=True))


if __name__ == "__main__":
    main()
