"""Offline-only ten-second Pi/Pironman/Flipper/ESP32 status snapshot model.

Accepts *synthetic or owner-supplied* bounded structured observations.
Never polls hardware, reads system files, opens ports or changes services.
No free-form labels, logs, device identifiers, network addresses or secrets.
"""
from dataclasses import dataclass

SOURCES = ("pi", "oled", "flipper", "esp32")
STATES = ("unknown", "observed", "disconnected", "unavailable")
MAX_AGE_SECONDS = 10


@dataclass(frozen=True)
class Status:
    source: str
    state: str
    age_seconds: int
    stale: bool


def summarize_snapshot(observations: dict[str, tuple[str, int]]) -> tuple[Status, ...]:
    """Validate observations and mark >10s evidence stale; missing is unknown.

    Ages are integer seconds (bool excluded); no timestamps, hardware identity,
    temperature, or credentials are accepted. Missing sources remain unknown.
    """
    if type(observations) is not dict or len(observations) > len(SOURCES):
        raise ValueError("expected bounded observation mapping")
    if any(type(key) is not str or key not in SOURCES for key in observations):
        raise ValueError("unsupported source")
    output = []
    for source in SOURCES:
        if source not in observations:
            output.append(Status(source, "unknown", 0, True))
            continue
        item = observations[source]
        if type(item) is not tuple or len(item) != 2:
            raise ValueError("invalid observation")
        state, age = item
        if type(state) is not str or state not in STATES:
            raise ValueError("invalid state")
        if type(age) is not int or not 0 <= age <= 86400:
            raise ValueError("invalid age")
        output.append(Status(source, state, age, age > MAX_AGE_SECONDS))
    return tuple(output)
