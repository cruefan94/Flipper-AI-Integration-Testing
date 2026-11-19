import tempfile
import unittest
from pathlib import Path
from pi_readonly_monitor import parse_meminfo, snapshot

class MonitorTests(unittest.TestCase):
    def test_memory_parsing(self):
        self.assertEqual(parse_meminfo('MemTotal: 4000 kB\nMemAvailable: 2500 kB'), {'MemTotal': 4000, 'MemAvailable': 2500})

    def test_missing_paths_are_safe(self):
        with tempfile.TemporaryDirectory() as d:
            s = snapshot(d)
            self.assertIsNone(s['temperature_c'])
            self.assertEqual(s['pironman_oled'], 'not_probed')

    def test_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name, value in [('proc/meminfo', 'MemTotal: 4096000 kB\nMemAvailable: 1024000 kB'), ('proc/uptime', '123.45 0'), ('sys/class/thermal/thermal_zone0/temp', '42500')]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(value)
            s = snapshot(d)
            self.assertEqual((s['temperature_c'], s['uptime_s'], s['memory_available_kib']), (42.5, 123, 1024000))

    def test_bad_values(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'sys/class/thermal/thermal_zone0'
            root.mkdir(parents=True)
            (root / 'temp').write_text('invalid')
            self.assertIsNone(snapshot(d)['temperature_c'])

if __name__ == '__main__':
    unittest.main()
