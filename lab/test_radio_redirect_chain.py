"""Offline public-safe radio redirect preflight. Never opens a network connection.

A real streaming client must separately enforce DNS/IP, TLS, redirect and
authorization policy at connection time. Syntax checks alone are insufficient.
"""
import unittest
from urllib.parse import urlsplit
from radio_feed_url_preflight import check_feed_url


def check_redirect_chain(urls, max_redirects=3):
    """Check a manually supplied absolute-URL chain; fail closed."""
    if not isinstance(max_redirects, int) or isinstance(max_redirects, bool) or max_redirects < 0 or max_redirects > 3:
        return False, 'invalid_redirect_limit'
    if not isinstance(urls, (list, tuple)) or not urls or len(urls) > max_redirects + 1:
        return False, 'invalid_chain_length'
    seen = set()
    initial_host = None
    for url in urls:
        valid, reason = check_feed_url(url)
        if not valid:
            return False, reason
        host = urlsplit(url).hostname.lower()
        if initial_host is None:
            initial_host = host
        if host != initial_host:
            return False, 'cross_host_redirect_requires_manual_approval'
        if url in seen:
            return False, 'redirect_loop'
        seen.add(url)
    return True, 'offline_syntax_only_not_network_or_legal_authorization'


class RedirectChainTests(unittest.TestCase):
    def test_single_url(self):
        self.assertTrue(check_redirect_chain(['https://radio.example.org/live'])[0])
    def test_same_host(self):
        self.assertTrue(check_redirect_chain(['https://radio.example.org/a', 'https://radio.example.org/b'])[0])
    def test_cross_host(self):
        self.assertFalse(check_redirect_chain(['https://radio.example.org/a', 'https://other.example.org/b'])[0])
    def test_localhost(self):
        self.assertFalse(check_redirect_chain(['https://radio.example.org/a', 'https://localhost/b'])[0])
    def test_http_downgrade(self):
        self.assertFalse(check_redirect_chain(['https://radio.example.org/a', 'http://radio.example.org/b'])[0])
    def test_ip_literal(self):
        self.assertFalse(check_redirect_chain(['https://radio.example.org/a', 'https://127.0.0.1/b'])[0])
    def test_loop(self):
        self.assertFalse(check_redirect_chain(['https://radio.example.org/a', 'https://radio.example.org/a'])[0])
    def test_hop_limit(self):
        self.assertFalse(check_redirect_chain(['https://radio.example.org/' + str(i) for i in range(5)])[0])
    def test_invalid_chain(self):
        for value in (None, 'https://radio.example.org/a', [], [None], [123]):
            self.assertFalse(check_redirect_chain(value)[0])
    def test_credentials(self):
        self.assertFalse(check_redirect_chain(['https://user:pass@radio.example.org/a'])[0])
    def test_invalid_limit(self):
        for limit in (None, '3', -1, 4, True):
            self.assertFalse(check_redirect_chain(['https://radio.example.org/a'], limit)[0])
    def test_zero_redirects(self):
        self.assertFalse(check_redirect_chain(['https://radio.example.org/a', 'https://radio.example.org/b'], 0)[0])


if __name__ == '__main__':
    unittest.main()
