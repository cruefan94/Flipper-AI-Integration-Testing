"""Read-only, non-identifying Pi USB serial-port inventory.

No device opens, subprocesses, privilege changes or hardware writes.
Device identity remains unconfirmed until separately verified by the owner.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def inventory(sys_tty_root: Path = Path("/sys/class/tty")) -> list[dict[str, str]]:
    """Enumerate candidate tty entries; never infer Flipper or ESP32 identity."""
    result = []
    try:
        entries = sorted(sys_tty_root.iterdir(), key=lambda p: p.name)
    except (OSError, ValueError):
        return result
    for entry in entries:
        name = entry.name
        if not (name.startswith("ttyACM") or name.startswith("ttyUSB")):
            continue
        suffix = name[6:] if name.startswith("ttyACM") else name[6:]
        if not suffix.isdecimal() or not entry.is_dir():
            continue
        result.append({
            "port": "/dev/" + name,
            "identity": "unconfirmed",
            "note": "Candidate USB serial interface; no device opened",
        })
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sys-tty-root", type=Path, default=Path("/sys/class/tty"),
                        help="Read-only sysfs root (or synthetic fixture directory)")
    args = parser.parse_args(argv)
    print(json.dumps({"interfaces": inventory(args.sys_tty_root),
                      "hardware_verified": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
