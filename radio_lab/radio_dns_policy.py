"""Offline IP-address vetting for receive-only HTTPS feeds; no DNS or sockets."""
import ipaddress


class UnsafeResolvedAddress(ValueError):
    """Resolved address set cannot be safely used for a public stream."""


def validate_resolved_addresses(addresses):
    """Validate every IP; caller must pin socket to vetted IP and recheck redirects.

    This is not a DNS rebinding defense by itself; no network operations occur.
    """
    if not isinstance(addresses, (tuple, list)) or not 1 <= len(addresses) <= 16:
        raise UnsafeResolvedAddress("invalid address count")
    normalized = []
    for raw in addresses:
        if not isinstance(raw, str) or not raw or raw.strip() != raw:
            raise UnsafeResolvedAddress("invalid address text")
        try:
            addr = ipaddress.ip_address(raw)
        except ValueError as exc:
            raise UnsafeResolvedAddress("invalid IP address") from exc
        if not addr.is_global or (isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped is not None):
            raise UnsafeResolvedAddress("non-public or mapped address")
        if str(addr) not in normalized:
            normalized.append(str(addr))
    return tuple(normalized)
