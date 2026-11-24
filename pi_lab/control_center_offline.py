"""Read-only control center composition from supplied evidence, not live polling."""
import unittest
from pi_lab.monitor_dashboard import render_rows
from pi_lab.offline_memory_summary import summarize_meminfo, render_summary
from pi_lab.pironman_service_evidence import summarize

def render_control_center(observations, meminfo=None, services=None):
    lines = ["Pi Control Center | OFFLINE EVIDENCE", "Device observations (10-second freshness threshold)"]
    for row in render_rows(observations):
        lines.append(f"{row.label}: {row.state} / {row.freshness}")
    lines.append(render_summary(summarize_meminfo(meminfo)) if meminfo is not None else "Memory: NOT OBSERVED")
    lines.append("Service configuration (not runtime status)")
    lines.extend(summarize(services if services is not None else ""))
    lines.append("Hardware controls: DISABLED")
    return "\n".join(lines)

class Tests(unittest.TestCase):
    def test_missing(self):
        report = render_control_center({})
        self.assertIn("Memory: NOT OBSERVED", report)
        self.assertIn("Pironman OLED: UNKNOWN / STALE", report)
        self.assertIn("Hardware controls: DISABLED", report)
    def test_combined(self):
        report = render_control_center({"pi": ("observed", 10), "esp32": ("observed", 11)}, "MemTotal: 1000 kB\nMemAvailable: 50 kB", "pironman.service enabled enabled")
        self.assertIn("Raspberry Pi: OBSERVED / FRESH", report)
        self.assertIn("ESP32: OBSERVED / STALE", report)
        self.assertIn("Memory pressure: HIGH", report)
        self.assertIn("pironman.service: enabled", report)
    def test_privacy(self):
        report = render_control_center({}, "MemTotal: 1000 kB\nMemAvailable: 500 kB\nHostname: secret", "secret.service enabled")
        self.assertNotIn("secret", report)
    def test_invalid(self):
        for args in [({"pi": ("observed", True)},), ({}, ""), ({}, None, "pironman.service running")]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                render_control_center(*args)

if __name__ == "__main__":
    unittest.main()
