"""Pure, offline Pi monitor frame assembly. No polling, I/O or device control.

The caller supplies health readings and optional redacted peripheral statuses.
A future owner-opt-in UI may request a new frame every 10 seconds.
"""
from dataclasses import dataclass
import unittest

from pi_health_snapshot_offline import summarize_health

PERIPHERALS = ("oled", "flipper", "esp32")
STATES = frozenset(("UNKNOWN", "CONNECTED", "DISCONNECTED", "STALE"))
MAX_AGE_SECONDS = 10


@dataclass(frozen=True)
class MonitorFrame:
    memory_used_percent: int
    available_mib: int
    load_1m: float
    health_status: str
    oled: str
    flipper: str
    esp32: str
    stale: bool


def assemble_frame(meminfo, loadavg, peripheral_states=None, *, age_seconds=0):
    """Return a redacted frame; fail closed on bad inputs or stale samples."""
    if type(age_seconds) not in (int, float) or not (0 <= age_seconds <= 86400):
        raise ValueError("invalid sample age")
    if peripheral_states is None:
        peripheral_states = {}
    if type(peripheral_states) is not dict or set(peripheral_states) - set(PERIPHERALS):
        raise ValueError("invalid peripheral inventory")
    if any(type(value) is not str or value not in STATES for value in peripheral_states.values()):
        raise ValueError("invalid peripheral state")
    health = summarize_health(meminfo, loadavg)
    stale = age_seconds > MAX_AGE_SECONDS
    values = {name: ("STALE" if stale else peripheral_states.get(name, "UNKNOWN"))
              for name in PERIPHERALS}
    return MonitorFrame(health.used_percent, health.available_mib,
                        health.load_1m, health.status,
                        values["oled"], values["flipper"], values["esp32"], stale)


class MonitorFrameTests(unittest.TestCase):
    MEM = "MemTotal: 4000000 kB\nMemAvailable: 2000000 kB"
    LOAD = "0.25 0.50 0.75 1/100 1234"

    def test_default_unknown(self):
        frame = assemble_frame(self.MEM, self.LOAD)
        self.assertEqual((frame.oled, frame.flipper, frame.esp32),
                         ("UNKNOWN", "UNKNOWN", "UNKNOWN"))
        self.assertEqual(frame.memory_used_percent, 50)

    def test_redacted_states(self):
        frame = assemble_frame(self.MEM, self.LOAD, {"flipper": "CONNECTED"})
        self.assertEqual(frame.flipper, "CONNECTED")
        self.assertNotIn("1234", repr(frame))

    def test_ten_second_boundary(self):
        self.assertFalse(assemble_frame(self.MEM, self.LOAD, age_seconds=10).stale)
        self.assertTrue(assemble_frame(self.MEM, self.LOAD, age_seconds=10.01).stale)

    def test_stale_fails_closed(self):
        frame = assemble_frame(self.MEM, self.LOAD, {"oled": "CONNECTED"}, age_seconds=11)
        self.assertEqual(frame.oled, "STALE")

    def test_reject_unknown_device(self):
        with self.assertRaises(ValueError):
            assemble_frame(self.MEM, self.LOAD, {"private_serial": "CONNECTED"})

    def test_reject_freeform_status(self):
        with self.assertRaises(ValueError):
            assemble_frame(self.MEM, self.LOAD, {"flipper": "serial 123"})

    def test_reject_invalid_age(self):
        for age in (-1, float("nan"), True, "10"):
            with self.subTest(age=age), self.assertRaises(ValueError):
                assemble_frame(self.MEM, self.LOAD, age_seconds=age)

    def test_bad_health_rejected(self):
        with self.assertRaises(ValueError):
            assemble_frame("broken", self.LOAD)


if __name__ == "__main__":
    unittest.main()
