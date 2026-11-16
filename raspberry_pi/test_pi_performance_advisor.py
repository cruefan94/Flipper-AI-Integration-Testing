"""Hardware-free performance advisor regression tests."""
import tempfile
import unittest
from pathlib import Path

from raspberry_pi.pi_performance_advisor import (
    parse_cpu_totals, parse_loadavg, parse_mem_kib, snapshot,
)


class PerformanceAdvisorTests(unittest.TestCase):
    def test_parsers_reject_bad_values(self):
        self.assertIsNone(parse_loadavg("NaN 1 2"))
        self.assertIsNone(parse_loadavg("-1 2 3"))
        self.assertIsNone(parse_cpu_totals("cpu 1 -1 3 4"))
        self.assertIsNone(parse_cpu_totals("cpu nonsense"))
        self.assertIsNone(parse_mem_kib("MemTotal: bad kB")["MemTotal"])

    def test_counters_not_percentages(self):
        self.assertEqual(parse_cpu_totals("cpu 10 20 30 40 5\n"),
                         {"total_ticks": 105, "idle_ticks": 45})
        self.assertEqual(parse_loadavg("0.20 0.50 1.00 1/100 20"), (0.2, 0.5, 1.0))

    def test_fixture_advice_and_no_modifications(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            proc = root / "proc"
            proc.mkdir()
            (proc / "meminfo").write_text(
                "MemTotal: 4096000 kB\nMemAvailable: 102400 kB\n"
                "SwapTotal: 1024000 kB\nSwapFree: 10240 kB\nCached: 200000 kB\n"
            )
            (proc / "stat").write_text("cpu 1 2 3 4 5\n")
            (proc / "loadavg").write_text("0.10 0.20 0.30 1/200 123\n")
            before = {p.name: p.read_bytes() for p in proc.iterdir()}
            result = snapshot(root)
            self.assertTrue(result["read_only"])
            self.assertEqual(len(result["advice"]), 2)
            self.assertEqual(before, {p.name: p.read_bytes() for p in proc.iterdir()})

    def test_missing_files_do_not_trigger_false_alarm(self):
        with tempfile.TemporaryDirectory() as directory:
            result = snapshot(Path(directory))
            self.assertIsNone(result["load_average_1_5_15"])
            self.assertEqual(result["advice"], [])


if __name__ == "__main__":
    unittest.main()
