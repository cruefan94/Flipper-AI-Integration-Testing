"""Consent-gated bridge between Pi /proc collector and 10-second freshness policy.

No polling loop, device I/O or controls. Other sources remain unknown until
independently validated adapters are supplied.
"""
from __future__ import annotations

from math import isfinite
from typing import Callable, Any

from raspberry_pi.pi_proc_collector import collect_pi_health
from raspberry_pi.pi_monitor_freshness import classify_snapshot


def sample_pi_monitor(*, consent: bool = False, now_seconds: float,
                      reader=None, collector: Callable[..., dict[str, Any]] = collect_pi_health
                      ) -> dict[str, Any]:
    """Take one authorized sample; timestamp only successfully parsed data.

    now_seconds is a caller-supplied monotonic timestamp. A freshness result
    never proves hardware health or permits cooling/device control.
    """
    if (isinstance(now_seconds, bool) or not isinstance(now_seconds, (int, float))
            or not isfinite(now_seconds)):
        raise ValueError("now_seconds must be finite monotonic seconds")
    snapshot = {}
    if consent:
        try:
            health = collector(consent=True, reader=reader)
            if (isinstance(health, dict)
                    and health.get("collection_status") == "read_only_sample_unverified"
                    and health.get("status") == "parsed_unverified"):
                snapshot["pi"] = {"observed_at": now_seconds}
        except (OSError, ValueError, TypeError):
            pass
    freshness = classify_snapshot(snapshot, now_seconds)
    freshness["pi_health"] = health if consent and "health" in locals() and isinstance(health, dict) else None
    freshness["sample_authorized"] = consent
    return freshness
