import unittest
from radio_dns_policy import UnsafeResolvedAddress, validate_resolved_addresses


class DNSPolicyTests(unittest.TestCase):
    def test_public_ipv4(self):
        self.assertEqual(validate_resolved_addresses(['8.8.8.8']), ('8.8.8.8',))

    def test_public_ipv6(self):
        self.assertEqual(validate_resolved_addresses(['2606:4700:4700::1111']), ('2606:4700:4700::1111',))

    def test_reject_mixed_private(self):
        with self.assertRaises(UnsafeResolvedAddress):
            validate_resolved_addresses(['8.8.8.8', '127.0.0.1'])

    def test_reject_link_local(self):
        with self.assertRaises(UnsafeResolvedAddress):
            validate_resolved_addresses(['169.254.1.2'])

    def test_reject_ipv4_mapped(self):
        with self.assertRaises(UnsafeResolvedAddress):
            validate_resolved_addresses(['::ffff:8.8.8.8'])

    def test_reject_empty_and_oversized(self):
        for case in ([], ['8.8.8.8'] * 17):
            with self.assertRaises(UnsafeResolvedAddress):
                validate_resolved_addresses(case)

    def test_reject_hostname_and_whitespace(self):
        for case in (['example.com'], [' 8.8.8.8']):
            with self.assertRaises(UnsafeResolvedAddress):
                validate_resolved_addresses(case)

    def test_deduplicate(self):
        self.assertEqual(validate_resolved_addresses(['8.8.8.8', '8.8.8.8']), ('8.8.8.8',))


if __name__ == '__main__':
    unittest.main()
