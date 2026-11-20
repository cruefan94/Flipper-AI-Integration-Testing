"""Synthetic, public-safe USB topology tests; no hardware or secrets."""
import unittest
from scripts.backpack_usb_topology import review

def topo(nodes, links):
    return {"nodes": nodes, "links": links}

PI = {"id":"pi","kind":"usb_host","powered":True}
ESP = {"id":"esp","kind":"device","powered":True}
UNPOWERED = {"id":"sensor","kind":"device","powered":False}

class TopologyTests(unittest.TestCase):
    def test_two_powered_endpoints_block(self):
        self.assertTrue(any("backfeed" in x for x in review(topo([PI,ESP],[{"a":"pi","b":"esp","kind":"usb","backfeed_blocked":False}]))))
    def test_isolation_claim_requires_verification(self):
        self.assertTrue(any("meter verification" in x for x in review(topo([PI,ESP],[{"a":"pi","b":"esp","kind":"usb","backfeed_blocked":True}]))))
    def test_unpowered_device_is_review_only(self):
        self.assertEqual(review(topo([PI,UNPOWERED],[{"a":"pi","b":"sensor","kind":"usb","backfeed_blocked":False}])),["review only: no physical wiring approval"])
    def test_missing_nodes_block(self):
        self.assertIn("no nodes",review(topo([],[])))
    def test_unknown_endpoint_block(self):
        self.assertIn("unknown or self-linked node",review(topo([PI],[{"a":"pi","b":"ghost","kind":"usb","backfeed_blocked":False}])))
    def test_duplicate_id_block(self):
        self.assertIn("duplicate node",review(topo([PI,PI],[])))
    def test_missing_blocked_flag_rejected(self):
        self.assertIn("invalid link",review(topo([PI,ESP],[{"a":"pi","b":"esp","kind":"usb"}])))
    def test_invalid_power_flag_rejected(self):
        self.assertIn("invalid node",review(topo([{"id":"x","kind":"device","powered":"false"}],[])))
    def test_signal_link_no_vbus_inference(self):
        self.assertEqual(review(topo([PI,ESP],[{"a":"pi","b":"esp","kind":"signal","backfeed_blocked":False}])),["review only: no physical wiring approval"])
    def test_invalid_document(self):
        self.assertIn("invalid topology document",review([]))

if __name__ == "__main__":
    unittest.main()
