"""Pure, hardware-free dashboard rows for the Pi lab monitor.

Consumes only validated structured observations from read_only_monitor.
No I/O, terminal control, hardware polling, device identity, or arbitrary labels.
"""
from dataclasses import dataclass

from pi_lab.read_only_monitor import SOURCES, Status, summarize_snapshot

LABELS = {"pi": "Raspberry Pi", "oled": "Pironman OLED",
          "flipper": "Flipper Zero", "esp32": "ESP32"}
STATES = {"unknown": "UNKNOWN", "observed": "OBSERVED",
          "disconnected": "DISCONNECTED", "unavailable": "UNAVAILABLE"}


@dataclass(frozen=True)
class DashboardRow:
    source: str
    label: str
    state: str
    freshness: str


def render_rows(observations: dict[str, tuple[str, int]]) -> tuple[DashboardRow, ...]:
    """Return fixed, privacy-minimal rows; stale evidence never reads as live."""
    statuses = summarize_snapshot(observations)
    return tuple(
        DashboardRow(
            source=item.source,
            label=LABELS[item.source],
            state=STATES[item.state],
            freshness="STALE" if item.stale else "FRESH",
        )
        for item in statuses
    )
