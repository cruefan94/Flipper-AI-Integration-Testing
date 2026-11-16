"""Offline URL admission check for lawful, receive-only public radio feeds.

No network access, streaming, transmission, or station discovery occurs here.
Only explicit HTTPS public-host URLs are eligible for later human review.
"""
from ipaddress import ip_address
from urllib.parse import urlsplit
import re

_HOST = re.compile(r"^(?=.{1,253}$)[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$", re.I)
_BLOCKED_SUFFIXES = (".local", ".internal", ".localhost", ".test", ".invalid", ".example")


def validate_public_feed_url(url: str) -> tuple[bool, str]:
    """Return eligibility for manual review, never a streaming authorization."""
    if not isinstance(url, str) or not url or len(url) > 2048 or url != url.strip():
        return False, "invalid input"
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.netloc:
            return False, "HTTPS required"
        if parsed.username is not None or parsed.password is not None:
            return False, "embedded credentials prohibited"
        if parsed.fragment:
            return False, "fragments prohibited"
        if parsed.port not in (None, 443):
            return False, "nonstandard port prohibited"
        host = parsed.hostname or ""
    except ValueError:
        return False, "malformed URL"
    if host.endswith(".") or host.lower().endswith(_BLOCKED_SUFFIXES):
        return False, "nonpublic hostname"
    try:
        ip_address(host)
        return False, "IP literal prohibited"
    except ValueError:
        pass
    if not _HOST.fullmatch(host):
        return False, "invalid public hostname"
    if "\\" in url or any(ord(c) < 32 or ord(c) == 127 for c in url):
        return False, "unsafe URL characters"
    return True, "eligible for manual lawful-source review only"
