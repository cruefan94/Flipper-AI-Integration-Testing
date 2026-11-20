"""Synthetic, offline regression tests for public-stream URL preflight."""
import unittest
from radio_feed_url_preflight import check_feed_url

class FeedUrlTests(unittest.TestCase):
    def test_safe_syntax(self):
        for value in ("https://example.org/live", "https://streams.example.org:443/feed?x=1"):
            self.assertTrue(check_feed_url(value)[0], value)
    def test_blocked(self):
        cases = [
            "http://example.org/feed", "ftp://example.org/feed",
            "https://localhost/live", "https://foo.local/live",
            "https://127.0.0.1/feed", "https://[::1]/feed",
            "https://192.168.1.5/feed", "https://user:pass@example.org/feed",
            "https://example.org:8080/feed", "https://example.org/#fragment",
            "https://example.org/hello world", "https://example.org/\\foo",
            "https://example.org:bad/feed", "https://intranet/feed",
            "", None, "https://example.org/" + "a" * 2048,
        ]
        for value in cases:
            with self.subTest(value=value):
                self.assertFalse(check_feed_url(value)[0])
    def test_no_authorization_claim(self):
        allowed, reason = check_feed_url("https://example.org/feed")
        self.assertTrue(allowed)
        self.assertIn("not_authorization", reason)

if __name__ == "__main__":
    unittest.main()
