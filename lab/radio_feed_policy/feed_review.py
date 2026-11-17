"""Offline, public-safe policy review for receive-only radio feed descriptors.

No network requests, device access, audio playback, or radio transmission.
Run: python3 -m unittest discover -s lab/radio_feed_policy -p 'test_*.py'
"""
from dataclasses import dataclass
from urllib.parse import urlsplit
import ipaddress
import re

ALLOWED_KINDS = frozenset({"am", "fm", "cb", "fire", "police"})
ALLOWED_TRANSPORTS = frozenset({"https"})
HOST_RE = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")


@dataclass(frozen=True)
class FeedReview:
    accepted: bool
    reason: str


def review_feed(descriptor: dict, approved_hosts: set[str]) -> FeedReview:
    """Review a user-curated, lawful, public receive-only feed descriptor.

    approved_hosts must be independently verified and explicitly supplied by
    the operator; no host is approved by default. This is not legal clearance.
    """
    if not isinstance(descriptor, dict):
        return FeedReview(False, "invalid_descriptor")
    if descriptor.get("kind") not in ALLOWED_KINDS:
        return FeedReview(False, "unsupported_kind")
    if descriptor.get("receive_only") is not True:
        return FeedReview(False, "receive_only_required")
    if descriptor.get("public_access_confirmed") is not True:
        return FeedReview(False, "public_access_unconfirmed")
    if descriptor.get("operator_authorized") is not True:
        return FeedReview(False, "authorization_unconfirmed")
    url = descriptor.get("url")
    if not isinstance(url, str) or not url or any(ord(c) < 33 or ord(c) == 127 for c in url):
        return FeedReview(False, "invalid_url")
    try:
        parsed = urlsplit(url)
        port = parsed.port
        host = (parsed.hostname or "").lower()
    except ValueError:
        return FeedReview(False, "invalid_url")
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        return FeedReview(False, "unsafe_transport")
    if port not in (None, 443) or not HOST_RE.fullmatch(host):
        return FeedReview(False, "invalid_host_or_port")
    try:
        ipaddress.ip_address(host)
        return FeedReview(False, "ip_literal_disallowed")
    except ValueError:
        pass
    if host not in approved_hosts or host not in {h.lower() for h in approved_hosts}:
        return FeedReview(False, "host_not_approved")
    if parsed.fragment or parsed.query:
        return FeedReview(False, "query_or_fragment_disallowed")
    if not parsed.path.startswith("/") or "//" in parsed.path:
        return FeedReview(False, "invalid_path")
    return FeedReview(True, "descriptor_policy_passed")
