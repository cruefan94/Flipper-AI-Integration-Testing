"""Owner-invoked, one-shot Pi health status; never controls hardware.

Run only on the owner's Pi with: python -m raspberry_pi.pi_health_once --consent
Without --consent, no kernel file is read. No background service or polling.
"""
from __future__ import annotations

import argparse
import json
import math
from typing import Callable, Any

from raspberry_pi.pi_proc_collector import collect_pi_health


def one_shot(*, consent: bool = False,
             collector: Callable[..., dict[str, Any]] = collect_pi_health
             ) -> dict[str, Any]:
    """Return bounded, non-identifying numeric status; never raw file contents."""
    if not isinstance(consent, bool):
        raise ValueError("consent must be boolean")
    if not consent:
        return {"status": "not_authorized", "pi": "unknown",
                "flipper": "unknown", "esp32": "unknown", "oled": "unknown"}
    try:
        sample = collector(consent=True)
    except (OSError, ValueError, TypeError, UnicodeError):
        sample = {}
    valid = (isinstance(sample, dict)
             and sample.get("collection_status") == "read_only_sample_unverified"
             and sample.get("status") == "parsed_unverified")
    result = {"status": "parsed_unverified" if valid else "unavailable",
              "pi": "sampled_unverified" if valid else "unknown",
              "flipper": "unknown", "esp32": "unknown", "oled": "unknown"}
    if valid:
        for key in ("memory_total_kib", "memory_available_kib",
                    "memory_used_percent", "uptime_seconds"):
            value = sample.get(key)
            if type(value) not in (int, float) or not math.isfinite(value):
                continue
            upper = 100 if key == "memory_used_percent" else 1e12
            if 0 <= value <= upper:
                result[key] = value
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="One-shot, read-only Pi health status")
    parser.add_argument("--consent", action="store_true",
                        help="authorize one read of /proc/meminfo and /proc/uptime")
    args = parser.parse_args(argv)
    print(json.dumps(one_shot(consent=args.consent), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
