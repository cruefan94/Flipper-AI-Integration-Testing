"""Offline validation of a radio stream redirect chain. Never performs network I/O."""
import ipaddress
from urllib.parse import urlsplit


class UnsafeFeedURL(ValueError):
    pass


def validate_feed_url(url: str) -> str:
    if not isinstance(url, str) or not url or url.strip() != url or any(ord(c) < 33 or ord(c) == 127 for c in url):
        raise UnsafeFeedURL('invalid URL text')
    try:
        p = urlsplit(url)
        host = p.hostname
        port = p.port
    except ValueError as exc:
        raise UnsafeFeedURL('malformed URL') from exc
    if p.scheme != 'https' or not host or p.username is not None or p.password is not None or p.fragment or port not in (None, 443):
        raise UnsafeFeedURL('URL policy violation')
    if '\\' in url or '%' in p.netloc or host.endswith('.') or '.' not in host:
        raise UnsafeFeedURL('ambiguous host')
    try:
        ipaddress.ip_address(host.strip('[]'))
    except ValueError:
        pass
    else:
        raise UnsafeFeedURL('IP literals prohibited')
    if any(not label or not label.replace('-', '').isalnum() or label.startswith('-') or label.endswith('-') for label in host.split('.')):
        raise UnsafeFeedURL('invalid hostname')
    return url


def validate_redirect_chain(urls: list[str], max_redirects: int = 3) -> tuple[str, ...]:
    """Validate all externally observed hops; caller must still pin DNS/IP at connect time."""
    if not isinstance(urls, (list, tuple)) or not 1 <= len(urls) <= max_redirects + 1:
        raise UnsafeFeedURL('invalid redirect count')
    return tuple(validate_feed_url(url) for url in urls)
