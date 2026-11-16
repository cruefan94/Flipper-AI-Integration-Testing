import unittest
from radio_redirect_policy import validate_redirect_chain, UnsafeFeedURL

class RedirectPolicyTests(unittest.TestCase):
    def test_https_public_chain(self):
        self.assertEqual(len(validate_redirect_chain(['https://feeds.example.org/live', 'https://cdn.example.net/stream'])), 2)

    def test_reject_redirect_to_private_ip(self):
        with self.assertRaises(UnsafeFeedURL):
            validate_redirect_chain(['https://feeds.example.org/live', 'https://192.168.1.1/admin'])

    def test_reject_redirect_to_http(self):
        with self.assertRaises(UnsafeFeedURL):
            validate_redirect_chain(['https://feeds.example.org/live', 'http://cdn.example.net/stream'])

    def test_reject_credentials(self):
        with self.assertRaises(UnsafeFeedURL):
            validate_redirect_chain(['https://user:pass@feeds.example.org/live'])

    def test_reject_too_many_hops(self):
        with self.assertRaises(UnsafeFeedURL):
            validate_redirect_chain(['https://feeds.example.org/live'] * 5)

    def test_reject_nonstandard_port(self):
        with self.assertRaises(UnsafeFeedURL):
            validate_redirect_chain(['https://feeds.example.org:8443/live'])

    def test_reject_control_char(self):
        with self.assertRaises(UnsafeFeedURL):
            validate_redirect_chain(['https://feeds.example.org/live\n'])

    def test_reject_ipv6_literal(self):
        with self.assertRaises(UnsafeFeedURL):
            validate_redirect_chain(['https://[::1]/live'])

if __name__ == '__main__':
    unittest.main()
