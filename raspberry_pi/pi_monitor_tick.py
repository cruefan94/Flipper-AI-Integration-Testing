"""Pure opt-in ten-second sampling policy for the Pi monitor.

No timers, threads, filesystem access, network, GPIO, or hardware controls.
The UI/event loop supplies monotonic timestamps and explicitly invokes tick().
"""
from __future__ import annotations

from math import isfinite
from typing import Any, Callable

from raspberry_pi.pi_monitor_adapter import sample_pi_monitor
from raspberry_pi.pi_monitor_freshness import INTERVAL_SECONDS, classify_snapshot


def _clock(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
        raise ValueError("clock must be finite, nonnegative monotonic seconds")
    return float(value)


def monitor_tick(*, consent: bool, now_seconds: float,
                 last_sample_at: float | None = None,
                 sampler: Callable[..., dict[str, Any]] = sample_pi_monitor
                 ) -> dict[str, Any]:
    """Return a safe polling decision and optional one-shot sample.

    No sample occurs without consent, before the ten-second interval, or if
    the clock moved backwards. The caller stores next_last_sample_at and must
    explicitly call again; this function never schedules itself.
    """
    now = _clock(now_seconds)
    last = None if last_sample_at is None else _clock(last_sample_at)
    if not isinstance(consent, bool):
        raise ValueError("consent must be boolean")
    if not consent:
        return {"sampled": False, "reason": "not_authorized",
                "next_last_sample_at": None,
                "monitor": classify_snapshot({}, now)}
    if last is not None and now < last:
        return {"sampled": False, "reason": "clock_regressed",
                "next_last_sample_at": None,
                "monitor": classify_snapshot({}, now)}
    if last is not None and now - last < INTERVAL_SECONDS:
        return {"sampled": False, "reason": "interval_pending",
                "next_last_sample_at": last,
                "monitor": classify_snapshot({}, now)}
    try:
        result = sampler(consent=True, now_seconds=now)
    except (OSError, ValueError, TypeError):
        result = classify_snapshot({}, now)
    if not isinstance(result, dict):
        result = classify_snapshot({}, now)
    return {"sampled": True, "reason": "sample_attempted_unverified",
            "next_last_sample_at": now, "monitor": result}
