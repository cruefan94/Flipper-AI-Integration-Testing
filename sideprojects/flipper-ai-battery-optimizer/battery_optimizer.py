"""Flipper AI Battery Optimizer v0.1 — isolated, read-only policy prototype.

Public-safe design. No BLE, GPIO, charging, power-register, or firmware writes.
The Android companion may eventually call this policy after receiving *opt-in*
telemetry from a compatible Flipper firmware adapter.
"""
from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Optional, Tuple


class Profile(str, Enum):
    ECO = "eco"
    BALANCED = "balanced"
    PERFORMANCE = "performance"


@dataclass(frozen=True)
class Telemetry:
    battery_pct: float
    charging: bool
    ble_connected: bool
    idle_seconds: int = 0
    active_operations: Tuple[str, ...] = ()
    temperature_c: Optional[float] = None
    sample_age_seconds: int = 0

    def __post_init__(self):
        if not isfinite(self.battery_pct) or not 0 <= self.battery_pct <= 100:
            raise ValueError("battery_pct must be 0..100")
        if not isinstance(self.charging, bool) or not isinstance(self.ble_connected, bool):
            raise ValueError("charging and ble_connected must be booleans")
        if self.idle_seconds < 0 or self.sample_age_seconds < 0:
            raise ValueError("elapsed seconds must be nonnegative")
        if isinstance(self.active_operations, (str, bytes)):
            raise ValueError("active_operations must be a tuple/list of strings")
        if len(self.active_operations) > 32 or any(
            not isinstance(op, str) or not op or len(op) > 64 for op in self.active_operations
        ):
            raise ValueError("active_operations contains an invalid label")
        if self.temperature_c is not None and (
            not isfinite(self.temperature_c) or not -20 <= self.temperature_c <= 85
        ):
            raise ValueError("temperature_c outside the accepted telemetry range")


@dataclass(frozen=True)
class Suggestion:
    key: str
    message: str
    priority: str = "normal"
    approval_required: bool = True


@dataclass(frozen=True)
class Analysis:
    profile: Profile
    status: str
    suggested_poll_seconds: int
    suggestions: Tuple[Suggestion, ...]
    can_apply_changes: bool = False


def analyze(sample: Telemetry, profile: Profile = Profile.BALANCED) -> Analysis:
    """Return *advice only*; do not perform changes on a Flipper or the phone.

    Stale telemetry suppresses battery advice instead of guessing. All suggestions
    require user approval, and this module never supplies executable device commands.
    """
    profile = Profile(profile)
    if sample.sample_age_seconds > 120:
        return Analysis(
            profile, "stale_telemetry", 900,
            (Suggestion("refresh_when_available",
                        "Use a fresh reading before recommending power changes."),),
        )

    active = bool(sample.active_operations)
    poll = 900 if (sample.idle_seconds >= 120 or sample.battery_pct <= 20) else 300
    if active:
        poll = max(poll, 300)  # Never force rapid polling during hardware tasks.
    if not sample.ble_connected:
        # Do not wake BLE repeatedly only to collect battery metrics.
        poll = max(poll, 900)

    advice = []
    if sample.temperature_c is not None and sample.temperature_c >= 45:
        advice.append(Suggestion(
            "elevated_temperature",
            "Battery telemetry shows elevated temperature; avoid optional heavy workloads and check the device.",
            "high",
        ))
    if not sample.charging and sample.battery_pct <= 15:
        advice.append(Suggestion(
            "low_battery",
            "Battery is low. Consider charging before starting long-running operations.",
            "high",
        ))
    if not sample.charging and sample.battery_pct <= 30 and profile != Profile.PERFORMANCE:
        advice.append(Suggestion(
            "prefer_eco",
            "Consider the Eco profile and a shorter screen-backlight timeout, if supported.",
        ))

    if not active and sample.idle_seconds >= 120 and profile != Profile.PERFORMANCE:
        advice.append(Suggestion(
            "idle_backlight",
            "If supported, shorten the backlight timeout during idle periods.",
        ))
    if not active and profile == Profile.ECO and not sample.charging:
        advice.append(Suggestion(
            "optional_accessory_standby",
            "If an accessory is truly idle, consider putting it into standby after user confirmation.",
        ))
    if active:
        advice.append(Suggestion(
            "preserve_active_task",
            "Keep current hardware operations running; do not interrupt active NFC, RF, IR, or GPIO tasks.",
        ))
    if sample.ble_connected:
        advice.append(Suggestion(
            "preserve_ble",
            "Maintain the current BLE session; do not disable it as a power-saving action.",
        ))
    else:
        advice.append(Suggestion(
            "no_forced_reconnect",
            "Avoid reconnecting Bluetooth solely to gather battery statistics.",
        ))

    return Analysis(profile, "advice_only", poll, tuple(advice))


def to_public_dict(analysis: Analysis) -> dict:
    """Minimal, non-sensitive advisory payload; intentionally excludes raw device identifiers."""
    return {
        "profile": analysis.profile.value,
        "status": analysis.status,
        "suggested_poll_seconds": analysis.suggested_poll_seconds,
        "can_apply_changes": False,
        "suggestions": [
            {"key": s.key, "message": s.message,
             "priority": s.priority, "approval_required": s.approval_required}
            for s in analysis.suggestions
        ],
    }
