"""Pure offline Pi memory summary; never reads hardware or OS state.

Only validated numeric memory fields and fixed advice enter the report.
"""
from dataclasses import dataclass
import unittest

from pi_lab.offline_memory_health import assess_meminfo
from pi_lab.offline_memory_advice import advise


@dataclass(frozen=True)
class MemorySummary:
    heading: str
    capacity: str
    pressure: str
    advice: str


def summarize_meminfo(evidence: str) -> MemorySummary:
    """Render a bounded, deterministic report from owner-supplied meminfo text."""
    health = assess_meminfo(evidence)
    guidance = advise(health)
    return MemorySummary(
        heading="Raspberry Pi memory (offline evidence)",
        capacity=f"Available: {health.available_percent}% ({health.available_kib} / {health.total_kib} KiB)",
        pressure=f"Memory pressure: {guidance.status}",
        advice=guidance.recommendation,
    )


def render_summary(summary: MemorySummary) -> str:
    """Accept only a report reproducible from its validated numeric fields."""
    if type(summary) is not MemorySummary:
        raise ValueError("MemorySummary required")
    if not all(type(v) is str for v in (summary.heading, summary.capacity, summary.pressure, summary.advice)):
        raise ValueError("invalid summary")
    # Fixed text is generated in summarize_meminfo; never render caller-forged fields.
    import re
    match = re.fullmatch(r"Available: ([0-9]{1,3})% \(([0-9]{1,10}) / ([0-9]{1,10}) KiB\)", summary.capacity)
    if match is None:
        raise ValueError("invalid capacity")
    percent, available, total = map(int, match.groups())
    expected = summarize_meminfo(f"MemTotal: {total} kB\\nMemAvailable: {available} kB".replace("\\n", "\n"))
    if summary != expected or percent != available * 100 // total:
        raise ValueError("inconsistent summary")
    return "\n".join((summary.heading, summary.capacity, summary.pressure, summary.advice))


class MemorySummaryTests(unittest.TestCase):
    def test_low(self):
        self.assertIn("Memory pressure: LOW", render_summary(summarize_meminfo("MemTotal: 1000 kB\nMemAvailable: 800 kB")))
    def test_moderate(self):
        self.assertIn("browser tabs", render_summary(summarize_meminfo("MemTotal: 1000 kB\nMemAvailable: 200 kB")))
    def test_high(self):
        self.assertIn("Memory pressure: HIGH", render_summary(summarize_meminfo("MemTotal: 1000 kB\nMemAvailable: 50 kB")))
    def test_ignore_private_extra_fields(self):
        output = render_summary(summarize_meminfo("Hostname: private\nMemTotal: 1000 kB\nMemAvailable: 500 kB"))
        self.assertNotIn("private", output)
    def test_reject_forged_summary(self):
        s = summarize_meminfo("MemTotal: 1000 kB\nMemAvailable: 500 kB")
        with self.assertRaises(ValueError):
            render_summary(MemorySummary(s.heading, s.capacity, s.pressure, "sudo reboot"))
    def test_reject_invalid_evidence(self):
        with self.assertRaises(ValueError):
            summarize_meminfo("MemTotal: 1000 kB\nMemAvailable: 2000 kB")
    def test_reject_untrusted_object(self):
        with self.assertRaises(ValueError):
            render_summary({"capacity": "hello"})


if __name__ == "__main__":
    unittest.main()
