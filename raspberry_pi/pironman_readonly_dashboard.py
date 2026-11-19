"""Read-only Pironman desktop view: direct Pi snapshot or local JSON file."""
import argparse
import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from pi.monitor.pi_readonly_monitor import snapshot as pi_snapshot

FIELDS = ("cpu_temp_c", "memory_available_mb", "memory_total_mb", "uptime_seconds",
          "pironman_oled", "flipper_usb", "esp32")
ALIASES = {"cpu_temp_c": "temperature_c", "uptime_seconds": "uptime_s"}
MEMORY_ALIASES = {"memory_available_mb": "memory_available_kib",
                  "memory_total_mb": "memory_total_kib"}


def normalize(payload):
    if not isinstance(payload, dict):
        raise ValueError("Snapshot must be a JSON object")
    result = {}
    for field in FIELDS:
        if field in payload:
            value = payload[field]
        elif field in MEMORY_ALIASES:
            kib = payload.get(MEMORY_ALIASES[field])
            value = round(kib / 1024, 1) if isinstance(kib, (int, float)) and not isinstance(kib, bool) and kib >= 0 else "not_probed"
        else:
            value = payload.get(ALIASES.get(field, field), "not_probed")
        if value is None or isinstance(value, (dict, list, bool)):
            value = "not_probed"
        result[field] = str(value)[:100]
    return result


def read_snapshot(path):
    path = Path(path)
    if path.stat().st_size > 65536:
        raise ValueError("Snapshot too large")
    return normalize(json.loads(path.read_text(encoding="utf-8")))


def read_live_snapshot():
    """Read proc/sysfs via the existing monitor, without writing any files."""
    return normalize(pi_snapshot())


class Dashboard:
    def __init__(self, root, snapshot=None):
        self.root, self.snapshot = root, Path(snapshot) if snapshot else None
        root.title("Pironman Lab — Read-only")
        root.geometry("620x420")
        ttk.Label(root, text="Pironman Lab | Read-only 10-second monitor",
                  font=("Sans", 14, "bold")).pack(pady=12)
        ttk.Label(root, text="Fan, RGB, OLED and device controls are disabled.").pack()
        frame = ttk.Frame(root, padding=18)
        frame.pack(fill="both", expand=True)
        self.labels = {}
        for field in FIELDS:
            line = ttk.Frame(frame)
            line.pack(fill="x", pady=5)
            ttk.Label(line, text=field.replace("_", " ").title(), width=27).pack(side="left")
            self.labels[field] = ttk.Label(line, text="not_probed")
            self.labels[field].pack(side="left")
        self.status = ttk.Label(root, text="Awaiting snapshot")
        self.status.pack(pady=8)
        self.refresh()

    def refresh(self):
        try:
            values = read_snapshot(self.snapshot) if self.snapshot else read_live_snapshot()
            for field, value in values.items():
                self.labels[field].config(text=value)
            self.status.config(text="Snapshot loaded (file may be stale)" if self.snapshot else "Live Pi read-only snapshot")
        except (OSError, ValueError) as exc:
            for label in self.labels.values():
                label.config(text="unavailable")
            self.status.config(text=f"Snapshot unavailable: {type(exc).__name__}")
        self.root.after(10000, self.refresh)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", nargs="?", help="Optional local JSON snapshot file; omitted = live read-only Pi")
    args = parser.parse_args()
    root = tk.Tk()
    Dashboard(root, args.snapshot)
    root.mainloop()
