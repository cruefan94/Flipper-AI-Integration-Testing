"""Offline, receive-only public radio-feed metadata gate.

No network requests, streaming, RF access, credentials, or transmission.
This is a planning gate, not legal authorization to monitor any feed.
"""
from urllib.parse import urlsplit
import ipaddress
import unittest

ALLOWED_KINDS = frozenset({"am", "fm", "cb", "fire", "police"})
ALLOWED_RIGHTS = frozenset({"public_authorized", "provider_permission"})

def validate_feed(record):
    """Return a list of reasons to reject a proposed feed metadata record."""
    errors = []
    if not isinstance(record, dict):
        return ["record must be an object"]
    if record.get("kind") not in ALLOWED_KINDS:
        errors.append("unsupported feed kind")
    if record.get("rights") not in ALLOWED_RIGHTS:
        errors.append("documented public access or provider permission required")
    if record.get("encrypted") is not False:
        errors.append("encrypted or unknown encryption state prohibited")
    if record.get("receive_only") is not True:
        errors.append("receive-only confirmation required")
    if record.get("provider") is None or not isinstance(record.get("provider"), str) or not record["provider"].strip():
        errors.append("named provider required")
    url = record.get("url")
    if not isinstance(url, str):
        return errors + ["HTTPS URL required"]
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
        if parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.fragment:
            errors.append("public HTTPS URL without credentials or fragment required")
        elif host.lower() == "localhost" or host.lower().endswith(".local"):
            errors.append("local endpoint prohibited")
        else:
            try:
                address = ipaddress.ip_address(host)
                if not address.is_global:
                    errors.append("non-public IP endpoint prohibited")
            except ValueError:
                if "." not in host or any(not label for label in host.split(".")):
                    errors.append("public DNS hostname required")
    except ValueError:
        errors.append("invalid URL")
    return errors

class FeedMetadataTests(unittest.TestCase):
    def setUp(self):
        self.valid = dict(kind="fm", rights="public_authorized", encrypted=False,
                          receive_only=True, provider="Example Broadcaster",
                          url="https://radio.example.org/live")
    def test_public_receive_only(self):
        self.assertEqual(validate_feed(self.valid), [])
    def test_each_kind(self):
        for kind in ALLOWED_KINDS:
            self.assertEqual(validate_feed(dict(self.valid, kind=kind)), [])
    def test_unknown_rights(self):
        self.assertTrue(validate_feed(dict(self.valid, rights="unknown")))
    def test_encryption(self):
        self.assertTrue(validate_feed(dict(self.valid, encrypted=True)))
    def test_missing_receive_only(self):
        self.assertTrue(validate_feed(dict(self.valid, receive_only=False)))
    def test_http(self):
        self.assertTrue(validate_feed(dict(self.valid, url="http://radio.example.org")))
    def test_private_ip(self):
        self.assertTrue(validate_feed(dict(self.valid, url="https://192.168.1.2/live")))
    def test_credentials(self):
        self.assertTrue(validate_feed(dict(self.valid, url="https://user:pass@radio.example.org/live")))
    def test_localhost(self):
        self.assertTrue(validate_feed(dict(self.valid, url="https://localhost/live")))
    def test_malformed(self):
        self.assertTrue(validate_feed([]))
    def test_missing_provider(self):
        self.assertTrue(validate_feed(dict(self.valid, provider="")))
    def test_no_network_or_transmit(self):
        self.assertFalse(any(name in globals() for name in ("requests", "socket", "transmit")))

if __name__ == "__main__":
    unittest.main()
