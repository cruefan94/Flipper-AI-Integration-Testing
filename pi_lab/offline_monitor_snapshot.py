"""Offline, read-only 10-second Pi lab monitor snapshot model.

No hardware, network, subprocess, file, GPIO, OLED, or service access.
Callers supply sanitized numeric observations. No background polling.
"""
from dataclasses import dataclass
from math import isfinite
import unittest

INTERVAL_SECONDS = 10
SOURCES = ("pi", "oled", "flipper", "esp32")
STATUSES = ("OK", "STALE", "MISSING", "INVALID")


@dataclass(frozen=True)
class SourceStatus:
    name: str
    status: str
    age_seconds: float | None


def evaluate_sources(now: object, observations: object) -> tuple[SourceStatus, ...]:
    """Return fixed-label status for each source; never echo supplied data."""
    if type(now) not in (int, float) or not isfinite(now) or now < 0:
        raise ValueError("invalid time")
    if type(observations) is not dict:
        raise ValueError("invalid observations")
    results = []
    for source in SOURCES:
        if source not in observations:
            results.append(SourceStatus(source, "MISSING", None))
            continue
        value = observations[source]
        if type(value) not in (int, float) or not isfinite(value) or value < 0 or value > now:
            results.append(SourceStatus(source, "INVALID", None))
            continue
        age = now - value
        results.append(SourceStatus(source, "OK" if age <= INTERVAL_SECONDS else "STALE", age))
    return tuple(results)


class OfflineMonitorTests(unittest.TestCase):
    def test_missing(self):
        self.assertEqual([x.status for x in evaluate_sources(100, {})], ["MISSING"] * 4)

    def test_all_fresh(self):
        self.assertEqual([x.status for x in evaluate_sources(100, dict.fromkeys(SOURCES, 100))], ["OK"] * 4)

    def test_boundary_fresh(self):
        self.assertEqual(evaluate_sources(100, {"pi": 90})[0].status, "OK")

    def test_stale(self):
        self.assertEqual(evaluate_sources(100, {"pi": 89.99})[0].status, "STALE")

    def test_future_rejected(self):
        self.assertEqual(evaluate_sources(100, {"pi": 101})[0].status, "INVALID")

    def test_negative_rejected(self):
        self.assertEqual(evaluate_sources(100, {"pi": -1})[0].status, "INVALID")

    def test_boolean_rejected(self):
        self.assertEqual(evaluate_sources(100, {"pi": True})[0].status, "INVALID")

    def test_nan_rejected(self):
        self.assertEqual(evaluate_sources(100, {"pi": float("nan")})[0].status, "INVALID")

    def test_infinity_rejected(self):
        self.assertEqual(evaluate_sources(100, {"pi": float("inf")})[0].status, "INVALID")

    def test_invalid_clock(self):
        with self.assertRaises(ValueError):
            evaluate_sources(float("nan"), {})

    def test_no_sensitive_echo(self):
        self.assertNotIn("secret-value", repr(evaluate_sources(100, {"pi": 99, "secret-value": "secret-value"})))

    def test_source_order(self):
        self.assertEqual(tuple(x.name for x in evaluate_sources(100, {})), SOURCES)


if __name__ == "__main__":
    unittest.main()
