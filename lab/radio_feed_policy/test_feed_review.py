import unittest
from feed_review import review_feed

BASE = {
    "kind": "fm",
    "receive_only": True,
    "public_access_confirmed": True,
    "operator_authorized": True,
    "url": "https://example.org/live",
}
HOSTS = {"example.org"}


class FeedPolicyTests(unittest.TestCase):
    def test_public_receive_only_descriptor(self):
        self.assertTrue(review_feed(BASE, HOSTS).accepted)

    def test_every_supported_category(self):
        for kind in ("am", "fm", "cb", "fire", "police"):
            self.assertTrue(review_feed({**BASE, "kind": kind}, HOSTS).accepted)

    def test_reject_transmit(self):
        self.assertFalse(review_feed({**BASE, "receive_only": False}, HOSTS).accepted)

    def test_reject_unverified_public_access(self):
        self.assertFalse(review_feed({**BASE, "public_access_confirmed": False}, HOSTS).accepted)

    def test_reject_missing_authorization(self):
        self.assertFalse(review_feed({**BASE, "operator_authorized": False}, HOSTS).accepted)

    def test_reject_unapproved_host(self):
        self.assertFalse(review_feed(BASE, set()).accepted)

    def test_reject_http(self):
        self.assertFalse(review_feed({**BASE, "url": "http://example.org/live"}, HOSTS).accepted)

    def test_reject_credentials(self):
        self.assertFalse(review_feed({**BASE, "url": "https://user:secret@example.org/live"}, HOSTS).accepted)

    def test_reject_query_token(self):
        self.assertFalse(review_feed({**BASE, "url": "https://example.org/live?token=secret"}, HOSTS).accepted)

    def test_reject_local_ip(self):
        self.assertFalse(review_feed({**BASE, "url": "https://127.0.0.1/live"}, {"127.0.0.1"}).accepted)

    def test_reject_nonstandard_port(self):
        self.assertFalse(review_feed({**BASE, "url": "https://example.org:8443/live"}, HOSTS).accepted)

    def test_reject_invalid_url(self):
        self.assertFalse(review_feed({**BASE, "url": "https://example.org:bad/live"}, HOSTS).accepted)

    def test_reject_unknown_kind(self):
        self.assertFalse(review_feed({**BASE, "kind": "transmit"}, HOSTS).accepted)


if __name__ == "__main__":
    unittest.main()
