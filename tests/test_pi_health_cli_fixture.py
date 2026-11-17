"""Read-only Pi health CLI integration checks using synthetic procfs files."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from raspberry_pi import pi_health_monitor


class PiHealthCliFixtureTests(unittest.TestCase):
    def test_once_reads_fixture_root_without_live_system_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proc = root / "proc"
            proc.mkdir()
            (proc / "uptime").write_text("123.9 0\n", encoding="utf-8")
            (proc / "meminfo").write_text(
                "MemTotal: 4096000 kB\nMemAvailable: 2048000 kB\n",
                encoding="utf-8",
            )
            output = io.StringIO()
            with patch.object(sys, "argv", ["pi_health_monitor", "--once", "--root", tmp]), \
                 patch.object(pi_health_monitor, "snapshot", wraps=pi_health_monitor.snapshot) as reader, \
                 contextlib.redirect_stdout(output):
                pi_health_monitor.main()
            reader.assert_called_once_with(root)
            data = json.loads(output.getvalue())
            self.assertEqual(data["uptime_seconds"], 123)
            self.assertEqual(data["memory"]["total_mib"], 4000)
            self.assertEqual(data["memory"]["available_mib"], 2000)
            self.assertIsNone(data["cpu_temp_c"])

    def test_short_interval_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(sys, "argv", [
                "pi_health_monitor", "--once", "--interval", "9", "--root", tmp
            ]), patch.object(pi_health_monitor, "snapshot") as reader, \
                 contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as failure:
                    pi_health_monitor.main()
            self.assertEqual(failure.exception.code, 2)
            reader.assert_not_called()


if __name__ == "__main__":
    unittest.main()
