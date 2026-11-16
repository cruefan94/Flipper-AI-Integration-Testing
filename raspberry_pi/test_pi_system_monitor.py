"""Synthetic tests for read-only Pi system monitor."""
import unittest
from unittest.mock import patch
import pi_system_monitor as monitor

class MonitorTests(unittest.TestCase):
    def test_meminfo(self):
        with patch.object(monitor,"read",return_value="MemTotal: 4000 kB\nMemAvailable: 1000 kB"):
            self.assertEqual(monitor.mem()["used_percent"],75.0)
    def test_temperature(self):
        with patch.object(monitor,"read",return_value="81500"):
            self.assertEqual(monitor.temp(),81.5)
    def test_missing_temperature(self):
        with patch.object(monitor,"read",return_value=None):
            self.assertIsNone(monitor.temp())
    def test_alerts(self):
        with patch.object(monitor,"temp",return_value=81),patch.object(monitor,"mem",return_value={"used_percent":91}),patch.object(monitor,"storage",return_value={"used_percent":92}),patch.object(monitor,"network",return_value={}),patch.object(monitor,"service",return_value="active"),patch.object(monitor,"qflipper_running",return_value=False):
            self.assertEqual(len(monitor.report()["alerts"]),3)

if __name__=="__main__": unittest.main()
