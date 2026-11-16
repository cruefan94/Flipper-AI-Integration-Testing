"""Read-only USB serial port panel for the Raspberry Pi workstation.

Uses sysfs inventory only. Does not open ports, read serial numbers, flash,
modify permissions, or infer that a detected board is definitely a Flipper.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

try:
    from .pi_usb_inventory import inventory
except ImportError:
    from pi_usb_inventory import inventory


def safe_label(value: object, fallback: str, limit: int = 96) -> str:
    """Keep untrusted USB descriptors on one printable, bounded display line."""
    if value is None or value == "":
        return fallback
    cleaned = "".join(ch if ch.isprintable() else " " for ch in str(value))
    cleaned = " ".join(cleaned.split())
    return cleaned[:limit] or fallback


def format_devices(devices: list[dict]) -> list[str]:
    """Conservatively display ports and non-unique USB descriptors."""
    rows = []
    for device in devices:
        port = safe_label(device.get("port"), "Unknown port", 48)
        vid = safe_label(device.get("vid"), "????", 12)
        pid = safe_label(device.get("pid"), "????", 12)
        product = safe_label(device.get("product"), "Unidentified USB serial device")
        rows.append(f"{port}  [{vid}:{pid}]  {product}")
    return rows or ["No ttyACM/ttyUSB serial ports detected."]


class UsbInventoryPanel(ttk.Frame):
    def __init__(self, parent, interval_ms: int = 10_000):
        if interval_ms < 10_000:
            raise ValueError("refresh interval must be at least 10 seconds")
        super().__init__(parent, padding=12)
        self.interval_ms = interval_ms
        self.timer_id = None
        self.closed = False
        ttk.Label(self, text="Read-only USB serial inventory (identity not verified)").pack(anchor="w")
        self.rows = tk.Listbox(self, width=84, height=8)
        self.rows.pack(fill="both", expand=True, pady=8)
        self.status = ttk.Label(self, text="No device ports are opened.")
        self.status.pack(anchor="w")
        ttk.Button(self, text="Refresh USB", command=self.refresh).pack(anchor="w", pady=5)
        self.refresh()

    def refresh(self):
        if self.closed:
            return
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        try:
            lines = format_devices(inventory())
            status = "Read-only inventory refreshed."
        except (OSError, ValueError, TypeError):
            lines = ["Unavailable — USB inventory failed."]
            status = "Read failed; previous devices cleared."
        self.rows.delete(0, tk.END)
        for line in lines:
            self.rows.insert(tk.END, line)
        self.status.configure(text=status)
        self.timer_id = self.after(self.interval_ms, self.refresh)

    def stop(self):
        self.closed = True
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None


def main():
    root = tk.Tk()
    root.title("Pironman Pi — USB Diagnostics")
    panel = UsbInventoryPanel(root)
    panel.pack(fill="both", expand=True)
    def close():
        panel.stop()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()


if __name__ == "__main__":
    main()
