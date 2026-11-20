"""Read-only qFlipper workstation readiness preflight (no USB/device access).

This reports tool availability only. It never launches qFlipper, enumerates
devices, opens USB, reads personal logs, or changes the Pi.
"""
from __future__ import annotations

import argparse
import json
import shutil
from typing import Callable


def preflight(*, consent: bool = False,
              which: Callable[[str], str | None] = shutil.which) -> dict[str, object]:
    if type(consent) is not bool:
        raise ValueError("consent must be boolean")
    if not consent:
        return {"status": "not_authorized", "qflipper": "unknown",
                "usb": "unknown", "backup": "unknown", "recovery": "unknown"}
    try:
        found = bool(which("qFlipper") or which("qflipper"))
    except (OSError, ValueError, TypeError):
        found = False
    return {"status": "local_tool_check_unverified",
            "qflipper": "available_on_path" if found else "not_found_on_path",
            "usb": "unknown", "backup": "unknown", "recovery": "unknown"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only qFlipper preflight")
    parser.add_argument("--consent", action="store_true",
                        help="allow local executable PATH lookup only")
    args = parser.parse_args(argv)
    print(json.dumps(preflight(consent=args.consent), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
