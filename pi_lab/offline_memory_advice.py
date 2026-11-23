"""Offline, advisory-only Pi 4B memory status. No OS reads or side effects.

Consumes the validated MemoryHealth from offline_memory_health. Never suggests
automatic process termination, cache clearing, swap edits, or service changes.
"""
from dataclasses import dataclass
import unittest

from pi_lab.offline_memory_health import MemoryHealth, assess_meminfo

@dataclass(frozen=True)
class MemoryAdvice:
    status: str
    available_percent: int
    recommendation: str

_MESSAGES = {
    "LOW": "Memory headroom is comfortable; leave working services unchanged.",
    "MODERATE": "Consider closing unused browser tabs manually; keep cooling and services running.",
    "HIGH": "Save browser work and consider closing unused tabs manually; do not kill services automatically.",
}

def advise(health: MemoryHealth) -> MemoryAdvice:
    if type(health) is not MemoryHealth:
        raise ValueError("validated MemoryHealth required")
    if (type(health.total_kib) is not int or type(health.available_kib) is not int
            or type(health.available_percent) is not int
            or health.total_kib <= 0 or not 0 <= health.available_kib <= health.total_kib):
        raise ValueError("invalid memory amounts")
    expected = assess_meminfo(
        f"MemTotal: {health.total_kib} kB\nMemAvailable: {health.available_kib} kB"
    )
    if (health.available_percent != expected.available_percent
            or health.pressure != expected.pressure):
        raise ValueError("inconsistent memory health")
    return MemoryAdvice(health.pressure, health.available_percent, _MESSAGES[health.pressure])

class MemoryAdviceTests(unittest.TestCase):
    def test_low(self):
        self.assertEqual(advise(assess_meminfo("MemTotal: 1000 kB\nMemAvailable: 800 kB")).status, "LOW")
    def test_moderate(self):
        self.assertIn("browser tabs", advise(assess_meminfo("MemTotal: 1000 kB\nMemAvailable: 200 kB")).recommendation)
    def test_high(self):
        self.assertIn("do not kill services", advise(assess_meminfo("MemTotal: 1000 kB\nMemAvailable: 50 kB")).recommendation)
    def test_reject_forged_classification(self):
        with self.assertRaises(ValueError):
            advise(MemoryHealth(1000, 50, 5, "LOW"))
    def test_reject_forged_percent(self):
        with self.assertRaises(ValueError):
            advise(MemoryHealth(1000, 500, 99, "LOW"))
    def test_reject_untrusted_type(self):
        with self.assertRaises(ValueError):
            advise({"pressure": "HIGH"})
    def test_reject_bool_amount(self):
        with self.assertRaises(ValueError):
            advise(MemoryHealth(True, 0, 0, "HIGH"))
    def test_fixed_output_no_hostnames(self):
        result = advise(assess_meminfo("Hostname: secret\nMemTotal: 1000 kB\nMemAvailable: 500 kB"))
        self.assertNotIn("secret", repr(result))
    def test_no_privileged_actions(self):
        for msg in _MESSAGES.values():
            self.assertNotIn("sudo", msg)
            self.assertNotIn("systemctl", msg)

if __name__ == "__main__":
    unittest.main()
