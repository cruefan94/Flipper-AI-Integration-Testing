"""Public-safe synthetic regression tests; no stream or network access."""
import unittest
from radio_provenance_preflight import assess


BASE = {
    "category": "FM",
    "source_url": "https://example.org/public-stream",
    "provider_name": "Synthetic Example",
    "public_listing_url": "https://example.org/listing",
    "reviewed_on": "2026-11-21",
    "reviewer_note": "Synthetic fixture only; not a real authorized feed",
    "receive_only": True,
    "encrypted": False,
    "access_review": "human_approved",
}


class ProvenanceTests(unittest.TestCase):
    def test_synthetic_review_ready(self):
        self.assertEqual(assess(BASE), [])

    def test_missing_human_review(self):
        self.assertIn("human_review_required", assess({**BASE, "access_review": "pending"}))

    def test_no_transmit(self):
        self.assertIn("not_receive_only", assess({**BASE, "receive_only": False}))

    def test_unknown_encryption(self):
        self.assertIn("encrypted_or_unknown", assess({**BASE, "encrypted": None}))

    def test_url_credentials(self):
        self.assertIn("unsafe_source_url", assess({**BASE, "source_url": "https://user:secret@example.org/a"}))

    def test_plain_http(self):
        self.assertIn("unsafe_source_url", assess({**BASE, "source_url": "http://example.org/a"}))

    def test_unknown_category(self):
        self.assertIn("unsupported_category", assess({**BASE, "category": "private"}))

    def test_missing_provider(self):
        self.assertIn("missing_provider_name", assess({**BASE, "provider_name": ""}))

    def test_non_object(self):
        self.assertIn("entry_not_object", assess(None))


if __name__ == "__main__":
    unittest.main()
