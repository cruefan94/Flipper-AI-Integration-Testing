"""Read-only Pironman desktop view for a local JSON snapshot. No GPIO writes."""
import argparse
import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk

FIELDS = ("cpu_temp_c", "memory_available_mb", "memory_total_mb", "uptime_seconds", "pironman_oled", "flipper_usb", "esp32")

def normalize(payload):
    if not isinstance(payload, dict):
        raise ValueError("Snapshot must be a JSON object")
    result = {}
    for field in FIELDS:
        value = payload.get(field, "not_probed")
        if value is None or isinstance(value, (dict, list)):
            value = "not_probed"
        result[field] = str(value)[:100]
    return result

def read_snapshot(path):
    path = Path(path)
    if path.stat().st_size > 65536:
        raise ValueError("Snapshot too large")
    return normalize(json.loads(path.read_text(encoding="utf-8")))

class Dashboard:
    def __init__(self, root, snapshot):
        self.root, self.snapshot = root, Path(snapshot)
        root.title("Pironman Lab — Read-only")
        root.geometry("620x420")
        ttk.Label(root, text="Pironman Lab | Read-only 10-second monitor", font=("Sans", 14, "bold")).pack(pady=12)
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
            values = read_snapshot(self.snapshot)
            for field, value in values.items():
                self.labels[field].config(text=value)
            self.status.config(text="Snapshot loaded (file-based; may be stale)")
        except (OSError, ValueError) as exc:
            for label in self.labels.values():
                label.config(text="unavailable")
            self.status.config(text=f"Snapshot unavailable: {type(exc).__name__}")
        self.root.after(10000, self.refresh)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", help="Local JSON snapshot file")
    args = parser.parse_args()
    root = tk.Tk()
    Dashboard(root, args.snapshot)
    root.mainloop()
