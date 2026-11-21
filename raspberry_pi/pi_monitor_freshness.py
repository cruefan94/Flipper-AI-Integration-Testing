"""Pure read-only status logic for a future 10-second Pi/Pironman monitor.

Consumes caller-supplied snapshots only. Does not poll GPIO, USB, BLE,
OLED, services, network, or devices. Never controls fans or RGB.
"""
from __future__ import annotations

from math import isfinite
from typing import Any, Mapping

INTERVAL_SECONDS = 10
SOURCES = ("pi", "pironman_oled", "flipper", "esp32")


def classify_snapshot(snapshot: Mapping[str, Any], now_seconds: float) -> dict[str, Any]:
    """Classify source freshness without trusting a reported 'connected' flag.

    A source is current only when its timestamp is a finite real number
    (excluding bool), non-future, and no older than 10 seconds.
    Missing sources are UNKNOWN, never 'offline' or 'healthy'.
    """
    if isinstance(now_seconds, bool) or not isinstance(now_seconds, (int, float)) or not isfinite(now_seconds):
        raise ValueError("now_seconds must be a finite numeric monotonic timestamp")
    status = {}
    for source in SOURCES:
        item = snapshot.get(source)
        if not isinstance(item, Mapping):
            status[source] = "unknown"
            continue
        stamp = item.get("observed_at")
        if isinstance(stamp, bool) or not isinstance(stamp, (int, float)) or not isfinite(stamp):
            status[source] = "unknown"
        elif stamp > now_seconds:
            status[source] = "invalid_future"
        elif now_seconds - stamp > INTERVAL_SECONDS:
            status[source] = "stale"
        else:
            status[source] = "fresh_unverified"
    return {
        "schema_version": 1,
        "interval_seconds": INTERVAL_SECONDS,
        "sources": status,
        "hardware_verified": False,
        "cooling_control_authorized": False,
        "device_commands_authorized": False,
    }
