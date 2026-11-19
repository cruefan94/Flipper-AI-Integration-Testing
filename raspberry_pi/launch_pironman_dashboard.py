"""CWD-independent, unprivileged entry point for the read-only Pironman view.

Usage: python3 /path/to/repo/raspberry_pi/launch_pironman_dashboard.py [snapshot.json]
       python3 /path/to/repo/raspberry_pi/launch_pironman_dashboard.py --check

--check only checks local source presence/syntax; it does NOT verify Pi hardware.
"""
import ast
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = ROOT / "raspberry_pi" / "pironman_readonly_dashboard.py"
MONITOR = ROOT / "pi" / "monitor" / "pi_readonly_monitor.py"


def check_sources():
    for source in (DASHBOARD, MONITOR):
        # Read-only syntax check; do not import Tk, probe hardware, or write pycache.
        ast.parse(source.read_text(encoding="utf-8"), filename=str(source))


def main():
    if sys.argv[1:] == ["--check"]:
        check_sources()
        print("Pi dashboard source check OK (not hardware validation)")
        return
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    runpy.run_module("raspberry_pi.pironman_readonly_dashboard", run_name="__main__")


if __name__ == "__main__":
    main()
