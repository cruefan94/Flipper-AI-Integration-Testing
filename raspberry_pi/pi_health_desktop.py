"""Read-only desktop viewer for Pi OS health snapshots.

Run on a Raspberry Pi desktop: python3 raspberry_pi/pi_health_desktop.py
No privileged commands, hardware writes, network listeners or device probing.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

try:
    from .pi_health_monitor import snapshot
except ImportError:
    from pi_health_monitor import snapshot


def format_snapshot(data: dict) -> dict[str, str]:
    memory = data.get("memory") or {}
    temp = data.get("cpu_temp_c")
    uptime = data.get("uptime_seconds")
    pressure = data.get("memory_pressure_some_avg10")
    def memory_value(available: str, total: str) -> str:
        left, right = memory.get(available), memory.get(total)
        if left is None or right is None or right == 0:
            return "Unavailable"
        return f"{left} / {right} MiB"

    return {
        "CPU temperature": "Unavailable" if temp is None else f"{temp:.1f} °C",
        "Available RAM": memory_value("available_mib", "total_mib"),
        "Free swap": memory_value("swap_free_mib", "swap_total_mib"),
        "Memory pressure (10 s)": "Unavailable" if pressure is None else f"{pressure:.2f}%",
        "Uptime": "Unavailable" if uptime is None else f"{uptime // 3600}h {(uptime % 3600) // 60}m",
    }


class PiHealthWindow:
    """Updates only labels; does not control Pi or Pironman hardware."""

    def __init__(self, root: tk.Tk, interval_ms: int = 10_000):
        if interval_ms < 10_000:
            raise ValueError("refresh interval must be at least 10 seconds")
        self.root = root
        self.interval_ms = interval_ms
        self.timer_id = None
        root.title("Pironman Pi Control Center — Read-only Health")
        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)
        self.labels = {}
        for row, name in enumerate(format_snapshot({})):
            ttk.Label(frame, text=name + ":").grid(row=row, column=0, sticky="w", padx=(0, 16), pady=5)
            value = ttk.Label(frame, text="Loading…")
            value.grid(row=row, column=1, sticky="w", pady=5)
            self.labels[name] = value
        self.status = ttk.Label(frame, text="Read-only. No Pironman settings are changed.")
        self.status.grid(row=len(self.labels), column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Button(frame, text="Refresh now", command=self.refresh).grid(
            row=len(self.labels) + 1, column=0, sticky="w", pady=(10, 0))
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.refresh()

    def refresh(self) -> None:
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        try:
            values = format_snapshot(snapshot())
            for name, value in values.items():
                self.labels[name].configure(text=value)
            self.status.configure(text="Read-only Pi OS health; refreshed successfully.")
        except (OSError, ValueError, TypeError) as exc:
            # Never leave previously successful numbers displayed as live data
            # after a failed refresh. A stale temperature can be dangerous.
            for label in self.labels.values():
                label.configure(text="Unavailable")
            self.status.configure(text=f"Read failed: {type(exc).__name__}; values cleared.")
        self.timer_id = self.root.after(self.interval_ms, self.refresh)

    def close(self) -> None:
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    PiHealthWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
