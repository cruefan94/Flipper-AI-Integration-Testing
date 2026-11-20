"""Offline one-shot CLI tests; no Pi kernel files or hardware accessed."""
import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from raspberry_pi.pi_health_once import one_shot, main


class OneShotTests(unittest.TestCase):
    def test_no_consent_no_collector(self):
        result = one_shot(collector=lambda **_: self.fail("unexpected read"))
        self.assertEqual(result["status"], "not_authorized")

    def test_explicit_consent_single_call(self):
        calls = []
        def collector(**kwargs):
            calls.append(kwargs)
            return {"collection_status": "read_only_sample_unverified",
                    "status": "parsed_unverified", "memory_total_kib": 4096,
                    "memory_available_kib": 2048, "memory_used_percent": 50.0,
                    "uptime_seconds": 10.0, "secret": "never print"}
        result = one_shot(consent=True, collector=collector)
        self.assertEqual(calls, [{"consent": True}])
        self.assertEqual(result["memory_available_kib"], 2048)
        self.assertNotIn("secret", result)
        for key in ("flipper", "esp32", "oled"):
            self.assertEqual(result[key], "unknown")

    def test_exception_unknown(self):
        def broken(**_):
            raise OSError("disconnected")
        self.assertEqual(one_shot(consent=True, collector=broken)["pi"], "unknown")

    def test_invalid_sample_unknown(self):
        self.assertEqual(one_shot(consent=True, collector=lambda **_: {})["status"], "unavailable")

    def test_cli_default_does_not_read(self):
        output = io.StringIO()
        with patch("raspberry_pi.pi_health_once.collect_pi_health", side_effect=AssertionError("read")):
            with redirect_stdout(output):
                self.assertEqual(main([]), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "not_authorized")

    def test_reject_nonboolean_consent(self):
        with self.assertRaises(ValueError):
            one_shot(consent=1)


if __name__ == "__main__":
    unittest.main()
