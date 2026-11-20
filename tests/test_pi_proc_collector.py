"""Offline tests; injected readers never touch real /proc or hardware."""
import unittest
from pathlib import Path
from raspberry_pi.pi_proc_collector import collect_pi_health

MEM = "MemTotal: 4096000 kB\nMemAvailable: 1024000 kB\n"
UP = "123.5 45.0"


class CollectorTests(unittest.TestCase):
    def test_denied_never_reads(self):
        def fail(_):
            raise AssertionError("read attempted without consent")
        result = collect_pi_health(reader=fail)
        self.assertEqual(result["collection_status"], "not_authorized")

    def test_consent_valid_sample(self):
        paths = []
        def reader(path):
            paths.append(str(path))
            return MEM if str(path) == "/proc/meminfo" else UP
        result = collect_pi_health(consent=True, reader=reader)
        self.assertEqual(paths, ["/proc/meminfo", "/proc/uptime"])
        self.assertEqual(result["memory_used_percent"], 75.0)
        self.assertEqual(result["collection_status"], "read_only_sample_unverified")
        self.assertFalse(result["hardware_verified"])
        self.assertFalse(result["cooling_control_authorized"])

    def test_unavailable_read(self):
        def fail(_):
            raise PermissionError("denied")
        self.assertEqual(collect_pi_health(consent=True, reader=fail)["collection_status"], "unavailable")

    def test_invalid_sample(self):
        self.assertEqual(collect_pi_health(consent=True, reader=lambda _: "bad")["status"], "unknown")

    def test_oversized_sample(self):
        self.assertEqual(collect_pi_health(consent=True, reader=lambda _: "x" * 65537)["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
