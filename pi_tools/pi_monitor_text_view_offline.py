"""Offline, read-only plain-text view for sanitized Pi monitor frames.

No polling, subprocesses, hardware access, network, or device writes.
Input must be an exact MonitorFrame from the validated offline model.
"""
import unittest

from pi_monitor_frame_offline import MonitorFrame, assemble_frame

ALLOWED_STATES = frozenset(("UNKNOWN", "CONNECTED", "DISCONNECTED", "STALE"))
ALLOWED_HEALTH = frozenset(("OBSERVED_NOT_DIAGNOSED", "LOW_AVAILABLE_MEMORY"))
# Restrict to the exact upstream health vocabulary; never render arbitrary labels.


def render_frame(frame):
    """Produce fixed-label output without identifiers, timestamps or raw readings."""
    if type(frame) is not MonitorFrame:
        raise ValueError("invalid monitor frame")
    if type(frame.stale) is not bool:
        raise ValueError("invalid stale flag")
    for name in ("oled", "flipper", "esp32"):
        state = getattr(frame, name)
        if type(state) is not str or state not in ALLOWED_STATES:
            raise ValueError("invalid peripheral status")
        if frame.stale and state != "STALE":
            raise ValueError("inconsistent stale status")
    if type(frame.memory_used_percent) is not int or not 0 <= frame.memory_used_percent <= 100:
        raise ValueError("invalid memory percentage")
    if type(frame.available_mib) is not int or not 0 <= frame.available_mib <= 1048576:
        raise ValueError("invalid available memory")
    if type(frame.load_1m) is not float or not 0 <= frame.load_1m <= 100000:
        raise ValueError("invalid load")
    if type(frame.health_status) is not str or frame.health_status not in ALLOWED_HEALTH:
        raise ValueError("invalid health status")
    return ("PI MONITOR (OFFLINE SNAPSHOT)\n"
            f"Memory used: {frame.memory_used_percent}%\n"
            f"Available memory: {frame.available_mib} MiB\n"
            f"CPU load (1m): {frame.load_1m:.2f}\n"
            f"Health: {frame.health_status}\n"
            f"OLED: {frame.oled}\n"
            f"Flipper: {frame.flipper}\n"
            f"ESP32: {frame.esp32}\n"
            f"Sample: {'STALE' if frame.stale else 'CURRENT'}\n")


class TextViewTests(unittest.TestCase):
    MEM = "MemTotal: 4000000 kB\nMemAvailable: 2000000 kB"
    LOAD = "0.25 0.50 0.75 1/100 1234"

    def frame(self, **kwargs):
        return assemble_frame(self.MEM, self.LOAD, **kwargs)

    def test_plain_snapshot(self):
        view = render_frame(self.frame())
        self.assertIn("Memory used: 50%", view)
        self.assertIn("Flipper: UNKNOWN", view)

    def test_status(self):
        self.assertIn("Flipper: CONNECTED", render_frame(self.frame(peripheral_states={"flipper": "CONNECTED"})))

    def test_stale(self):
        view = render_frame(self.frame(age_seconds=11))
        self.assertIn("Sample: STALE", view)
        self.assertIn("OLED: STALE", view)

    def test_no_identifiers(self):
        view = render_frame(self.frame())
        self.assertNotIn("1234", view)
        self.assertNotIn("serial", view.lower())

    def test_reject_wrong_object(self):
        with self.assertRaises(ValueError):
            render_frame({"flipper": "CONNECTED"})

    def test_reject_injected_status(self):
        from dataclasses import replace
        with self.assertRaises(ValueError):
            render_frame(replace(self.frame(), flipper="CONNECTED\\nsecret"))

    def test_reject_inconsistent_stale(self):
        from dataclasses import replace
        with self.assertRaises(ValueError):
            render_frame(replace(self.frame(age_seconds=11), oled="CONNECTED"))

    def test_reject_unknown_health_status(self):
        from dataclasses import replace
        for status in ("SECRET", "DEVICE_SERIAL", "OK\\nprivate", "", 1, None):
            with self.subTest(status=status), self.assertRaises(ValueError):
                render_frame(replace(self.frame(), health_status=status))

    def test_upstream_health_contract(self):
        from pi_health_snapshot_offline import summarize_health
        self.assertEqual(ALLOWED_HEALTH, frozenset((
            summarize_health(self.MEM, self.LOAD).status,
            summarize_health("MemTotal: 4000000 kB\nMemAvailable: 100000 kB", self.LOAD).status,
        )))

    def test_accept_all_known_health_labels(self):
        from dataclasses import replace
        for status in ALLOWED_HEALTH:
            with self.subTest(status=status):
                self.assertIn(f"Health: {status}", render_frame(replace(self.frame(), health_status=status)))

    def test_reject_invalid_metrics(self):
        from dataclasses import replace
        with self.assertRaises(ValueError):
            render_frame(replace(self.frame(), memory_used_percent=101))


if __name__ == "__main__":
    unittest.main()
