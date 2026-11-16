"""Synthetic offline checks; no real radio URLs or network calls."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from radio_feed_url_safety import validate_public_feed_url


class FeedURLSafetyTests(unittest.TestCase):
    def test_public_https_host_eligible_for_review(self):
        self.assertTrue(validate_public_feed_url("https://radio.example.org/live")[0])

    def test_plain_http_rejected(self):
        self.assertFalse(validate_public_feed_url("http://radio.example.org/live")[0])

    def test_private_and_loopback_ip_rejected(self):
        for url in ("https://127.0.0.1/live", "https://192.168.1.5/live",
                    "https://[::1]/live", "https://8.8.8.8/live"):
            with self.subTest(url=url):
                self.assertFalse(validate_public_feed_url(url)[0])

    def test_credentials_and_custom_ports_rejected(self):
        for url in ("https://user:secret@radio.example.org/live",
                    "https://radio.example.org:8080/live"):
            with self.subTest(url=url):
                self.assertFalse(validate_public_feed_url(url)[0])

    def test_local_and_invalid_host_rejected(self):
        for url in ("https://device.local/feed", "https://localhost/feed",
                    "https://radio.example.org./feed", "https://singlelabel/feed"):
            with self.subTest(url=url):
                self.assertFalse(validate_public_feed_url(url)[0])

    def test_malformed_and_unsafe_rejected(self):
        for url in ("", " https://radio.example.org/live",
                    "https://radio.example.org/live#fragment",
                    "https://radio.example.org/\\@localhost",
                    "https://radio.example.org/\nfeed"):
            with self.subTest(url=url):
                self.assertFalse(validate_public_feed_url(url)[0])


if __name__ == "__main__":
    unittest.main()
