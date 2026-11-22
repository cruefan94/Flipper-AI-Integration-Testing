"""Offline-only metadata gate for lawful, receive-only radio feed catalog entries.

No network, SDR, radio transmit, audio capture, or device access.
This is a conservative catalog preflight, not legal authorization.
"""
from urllib.parse import urlsplit
import ipaddress
import unittest

ALLOWED_KINDS = {"am", "fm", "cb", "fire", "police"}
ALLOWED_TRANSPORTS = {"public_https_stream", "public_https_directory"}

def validate_feed(entry):
    if not isinstance(entry, dict):
        return False, "entry_not_object"
    if set(entry) != {"kind", "transport", "url", "public_access", "receive_only", "provider_permission"}:
        return False, "schema_mismatch"
    if entry["kind"] not in ALLOWED_KINDS or entry["transport"] not in ALLOWED_TRANSPORTS:
        return False, "unsupported_feed"
    if entry["public_access"] is not True or entry["receive_only"] is not True or entry["provider_permission"] is not True:
        return False, "authorization_unverified"
    url = entry["url"]
    if not isinstance(url, str) or len(url) > 2048 or any(ord(c) < 33 or ord(c) == 127 for c in url):
        return False, "invalid_url"
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
        if parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.port not in (None, 443):
            return False, "unsafe_url"
        if host.lower() in {"localhost", "localhost.localdomain"} or host.lower().endswith((".local", ".internal", ".localhost")):
            return False, "local_host"
        try:
            ipaddress.ip_address(host)
            return False, "ip_literal"
        except ValueError:
            pass
        if "." not in host or not all(label and len(label) <= 63 and label[0].isalnum() and label[-1].isalnum() and all(ch.isascii() and (ch.isalnum() or ch == "-") for ch in label) for label in host.split(".")):
            return False, "invalid_hostname"
    except (ValueError, TypeError):
        return False, "invalid_url"
    return True, "metadata_pass_only"

class FeedPolicyTests(unittest.TestCase):
    def setUp(self):
        self.valid = dict(kind="fm", transport="public_https_stream",
                          url="https://example.org/listen", public_access=True,
                          receive_only=True, provider_permission=True)
    def check(self, key, value):
        x = self.valid.copy()
        x[key] = value
        self.assertFalse(validate_feed(x)[0])
    def test_valid_metadata_only(self):
        self.assertEqual(validate_feed(self.valid), (True, "metadata_pass_only"))
    def test_reject_transmission(self):
        self.check("receive_only", False)
    def test_reject_permission_unknown(self):
        self.check("provider_permission", False)
    def test_reject_nonpublic(self):
        self.check("public_access", False)
    def test_reject_unsupported_kind(self):
        self.check("kind", "encrypted_police")
    def test_reject_transport(self):
        self.check("transport", "sdr_transmit")
    def test_reject_http(self):
        self.check("url", "http://example.org/listen")
    def test_reject_credentials(self):
        self.check("url", "https://user:pass@example.org/listen")
    def test_reject_localhost(self):
        self.check("url", "https://localhost/listen")
    def test_reject_private_ip(self):
        self.check("url", "https://192.168.1.1/listen")
    def test_reject_query_token(self):
        self.check("url", "https://example.org/listen?token=not-a-real-token")
    def test_reject_query_parameter(self):
        self.check("url", "https://example.org/listen?station=1")
    def test_reject_fragment(self):
        self.check("url", "https://example.org/listen#token")
    def test_reject_bad_schema(self):
        x = self.valid.copy()
        x["secret"] = "no"
        self.assertFalse(validate_feed(x)[0])

if __name__ == "__main__":
    unittest.main()
