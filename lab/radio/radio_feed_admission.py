#!/usr/bin/env python3
"""Offline metadata admission gate for lawful receive-only radio feed catalogues.

No network, radio, subprocess, credentials, device access, or playback.
This checks operator-supplied metadata, not the actual lawfulness of a stream.
"""
import json
import sys
import unittest
from urllib.parse import urlsplit

CATEGORIES = {"am", "fm", "cb", "fire", "police"}
REQUIRED = {"category", "url", "receive_only", "public_access_confirmed", "authorization_reviewed", "encrypted"}


def validate(entry):
    if not isinstance(entry, dict):
        return ["entry_not_object"]
    issues = []
    if not REQUIRED.issubset(entry):
        issues.append("missing_required_fields")
    if entry.get("category") not in CATEGORIES:
        issues.append("unsupported_category")
    if entry.get("receive_only") is not True:
        issues.append("not_receive_only")
    if entry.get("public_access_confirmed") is not True:
        issues.append("public_access_unconfirmed")
    if entry.get("authorization_reviewed") is not True:
        issues.append("authorization_review_missing")
    if entry.get("encrypted") is not False:
        issues.append("encryption_unknown_or_present")
    url = entry.get("url")
    if not isinstance(url, str):
        issues.append("invalid_url")
    else:
        try:
            p = urlsplit(url)
            if p.scheme != "https" or not p.hostname or p.username or p.password or p.fragment or p.port not in (None, 443):
                issues.append("unsafe_url")
            if p.hostname and (p.hostname == "localhost" or p.hostname.endswith(".local")):
                issues.append("local_address_not_allowed")
        except ValueError:
            issues.append("invalid_url")
    return issues


class Tests(unittest.TestCase):
    def setUp(self):
        self.good = dict(category="fm", url="https://example.org/live", receive_only=True,
                         public_access_confirmed=True, authorization_reviewed=True, encrypted=False)

    def test_valid_metadata(self):
        self.assertEqual(validate(self.good), [])

    def test_no_public_confirmation(self):
        self.assertIn("public_access_unconfirmed", validate({**self.good, "public_access_confirmed": False}))

    def test_no_authorization_review(self):
        self.assertIn("authorization_review_missing", validate({**self.good, "authorization_reviewed": False}))

    def test_encrypted(self):
        self.assertIn("encryption_unknown_or_present", validate({**self.good, "encrypted": True}))

    def test_not_receive_only(self):
        self.assertIn("not_receive_only", validate({**self.good, "receive_only": False}))

    def test_http(self):
        self.assertIn("unsafe_url", validate({**self.good, "url": "http://example.org"}))

    def test_credentials(self):
        self.assertIn("unsafe_url", validate({**self.good, "url": "https://user:secret@example.org"}))

    def test_unknown_category(self):
        self.assertIn("unsupported_category", validate({**self.good, "category": "private"}))

    def test_missing_fields(self):
        self.assertIn("missing_required_fields", validate({}))

    def test_local_url(self):
        self.assertIn("local_address_not_allowed", validate({**self.good, "url": "https://localhost/feed"}))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 2:
        with open(sys.argv[1], encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise SystemExit("Expected a JSON array of metadata records")
        results = [{"index": i, "issues": validate(item)} for i, item in enumerate(data)]
        print(json.dumps(results, indent=2))
        raise SystemExit(1 if any(item["issues"] for item in results) else 0)
    else:
        raise SystemExit("Usage: python3 radio_feed_admission.py --self-test | metadata.json")
