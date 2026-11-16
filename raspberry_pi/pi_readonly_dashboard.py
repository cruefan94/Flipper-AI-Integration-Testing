"""Combined read-only Pi health and USB diagnostics desktop.

No privileged operations, serial port opens, device writes, or network listeners.
Run: python3 -m raspberry_pi.pi_readonly_dashboard
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .pi_health_desktop import format_snapshot, snapshot
from .pi_usb_desktop import UsbInventoryPanel


class HealthPanel(ttk.Frame):
    def __init__(self, parent, interval_ms: int = 10_000):
        if interval_ms < 10_000:
            raise ValueError("refresh interval must be at least 10 seconds")
        super().__init__(parent, padding=12)
        self.interval_ms = interval_ms
        self.timer_id = None
        self.closed = False
        self.labels = {}
        for index, name in enumerate(format_snapshot({})):
            ttk.Label(self, text=name + ":").grid(row=index, column=0, sticky="w", padx=8, pady=4)
            label = ttk.Label(self, text="Unavailable")
            label.grid(row=index, column=1, sticky="w")
            self.labels[name] = label
        self.status = ttk.Label(self, text="Read-only health")
        self.status.grid(row=len(self.labels), column=0, columnspan=2, sticky="w")
        ttk.Button(self, text="Refresh health", command=self.refresh).grid(
            row=len(self.labels) + 1, column=0, sticky="w", pady=8
        )
        self.refresh()

    def refresh(self):
        if self.closed:
            return
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        try:
            values = format_snapshot(snapshot())
            for name, label in self.labels.items():
                label.configure(text=values.get(name, "Unavailable"))
            self.status.configure(text="Read-only health refreshed.")
        except (OSError, ValueError, TypeError) as exc:
            for label in self.labels.values():
                label.configure(text="Unavailable")
            self.status.configure(text=f"Health unavailable ({type(exc).__name__}); stale values cleared.")
        self.timer_id = self.after(self.interval_ms, self.refresh)

    def stop(self):
        self.closed = True
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None


def main():
    root = tk.Tk()
    root.title("Pironman Pi — Read-only Health and USB")
    tabs = ttk.Notebook(root)
    tabs.pack(fill="both", expand=True)
    health = HealthPanel(tabs)
    usb = UsbInventoryPanel(tabs)
    tabs.add(health, text="Pi health")
    tabs.add(usb, text="USB diagnostics")

    def close():
        health.stop()
        usb.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()


if __name__ == "__main__":
    main()
