"""Offline URL preflight for user-approved, receive-only public radio streams.

This checks URL syntax and conservative network destinations. It does NOT
establish broadcast legality, licensing, feed authorization, or availability.
No network connections, playback, SDR, radio transmit or hardware access.
"""
import ipaddress
from urllib.parse import urlsplit

MAX_URL_LENGTH = 2048

def check_feed_url(url):
    """Return (allowed, reason); fail closed on uncertain URLs."""
    if not isinstance(url, str) or not url or len(url) > MAX_URL_LENGTH:
        return False, "invalid_length_or_type"
    if any(ord(c) < 33 or ord(c) == 127 for c in url):
        return False, "control_or_whitespace"
    try:
        parsed = urlsplit(url)
        if parsed.scheme.lower() != "https":
            return False, "https_required"
        if not parsed.hostname or parsed.username is not None or parsed.password is not None:
            return False, "host_or_credentials"
        if parsed.port not in (None, 443):
            return False, "nonstandard_port"
        host = parsed.hostname
        if host.endswith(".") or host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
            return False, "local_host"
        if not host.isascii() or not all(part and len(part) <= 63 and part.replace("-", "").isalnum() and not part.startswith("-") and not part.endswith("-") for part in host.split(".")):
            return False, "invalid_hostname"
        try:
            ipaddress.ip_address(host)
            return False, "ip_literal_not_allowed"
        except ValueError:
            pass
        if "." not in host:
            return False, "public_dns_name_required"
        if "\\" in url or "#" in url:
            return False, "ambiguous_url"
        return True, "url_syntax_only_not_authorization"
    except (ValueError, UnicodeError):
        return False, "malformed_url"
