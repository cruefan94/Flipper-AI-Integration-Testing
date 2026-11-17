"""Read-only browser RAM guidance tab for the Pi desktop dashboard."""
from __future__ import annotations

from tkinter import ttk

from .pi_browser_memory_advisor import snapshot


def format_budget(data: dict) -> tuple[str, str]:
    """Fail closed on unavailable or malformed snapshots."""
    if not isinstance(data, dict) or data.get("status") not in (
        "comfortable", "constrained", "critical"
    ):
        return "Unavailable", "Memory readings unavailable; no changes performed."
    total, available = data.get("total_mib"), data.get("available_mib")
    if (not isinstance(total, int) or isinstance(total, bool) or total <= 0
            or not isinstance(available, int) or isinstance(available, bool)
            or available < 0 or available > total):
        return "Unavailable", "Memory readings unavailable; no changes performed."
    advice = data.get("recommendations")
    if not isinstance(advice, list) or not advice or not all(
        isinstance(item, str) for item in advice
    ):
        return "Unavailable", "Memory readings unavailable; no changes performed."
    return (
        f"{data['status'].capitalize()} — {available} / {total} MiB available",
        " ".join(advice),
    )


class BrowserAdvicePanel(ttk.Frame):
    def __init__(self, parent, interval_ms: int = 10_000):
        if interval_ms < 10_000:
            raise ValueError("refresh interval must be at least 10 seconds")
        super().__init__(parent, padding=12)
        self.interval_ms = interval_ms
        self.timer_id = None
        self.closed = False
        self.memory = ttk.Label(self, text="Unavailable")
        self.memory.pack(anchor="w", pady=6)
        self.advice = ttk.Label(self, text="Read-only advice", wraplength=560)
        self.advice.pack(anchor="w", pady=6)
        ttk.Button(self, text="Refresh advice", command=self.refresh).pack(anchor="w")
        self.refresh()

    def refresh(self):
        if self.closed:
            return
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        try:
            summary, advice = format_budget(snapshot())
        except (OSError, ValueError, TypeError):
            summary, advice = format_budget({})
        self.memory.configure(text=summary)
        self.advice.configure(text=advice)
        self.timer_id = self.after(self.interval_ms, self.refresh)

    def stop(self):
        self.closed = True
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
