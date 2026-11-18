import subprocess
import unittest
from unittest.mock import Mock
import pi_usb_crash_triage as triage

class TriageTests(unittest.TestCase):
    def test_bounded_readonly_commands(self):
        seen = []
        def fake(argv, **kwargs):
            seen.append((argv, kwargs))
            return Mock(returncode=0, stdout='ok', stderr='')
        data = triage.collect(fake)
        self.assertEqual(set(data), set(triage.CHECKS))
        for argv, opts in seen:
            self.assertIsInstance(argv, list)
            self.assertFalse(opts.get('shell', False))
            self.assertLessEqual(opts['timeout'], 8)
            self.assertFalse(any(a in argv for a in ('sudo', 'rm', 'flash', 'reboot')))
    def test_failure_is_reported(self):
        def fake(argv, **kwargs):
            raise subprocess.TimeoutExpired(argv, 8)
        self.assertTrue(all(x['error'] == 'TimeoutExpired' for x in triage.collect(fake).values()))
    def test_power_flags_distinguish_current_historical(self):
        self.assertTrue(triage.analyze({'power': {'output':'throttled=0x10000'}})['historical_undervoltage_flag'])
        self.assertFalse(triage.analyze({'power': {'output':'throttled=0x10000'}})['current_undervoltage_flag'])
    def test_crash_clues_are_not_conclusions(self):
        signals = triage.analyze({'log': {'output': 'usb disconnect; oom-killer; labwc segfault'}})
        self.assertTrue(signals['usb_reset'])
        self.assertTrue(signals['out_of_memory'])
        self.assertTrue(signals['desktop_failure'])

    def test_current_kernel_events_are_collected(self):
        self.assertIn('current_kernel_usb', triage.CHECKS)
        self.assertIn('previous_kernel_usb', triage.CHECKS)
        def fake(argv, **kwargs):
            message = 'usb 1-1: USB disconnect' if argv == triage.CHECKS['current_kernel_usb'] else ''
            return Mock(returncode=0, stdout=message, stderr='')
        self.assertTrue(triage.analyze(triage.collect(fake))['usb_reset'])

    def test_large_output_truncated(self):
        p = triage.bounded_run(['python3', '-c', 'print("x" * 100000)'], timeout=8)
        self.assertEqual(p.returncode, 0)
        self.assertLessEqual(len(p.stdout), 6000)

if __name__ == '__main__':
    unittest.main()
