import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

class PublicContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=json.loads((ROOT/"contracts/ai_satellite_v1.json").read_text(encoding="utf-8"))

    def test_version_and_transport(self):
        self.assertEqual(self.contract["schema_version"],1)
        self.assertIn("ble",self.contract["transport"])
        self.assertIn("wifi",self.contract["transport"])

    def test_request_reply_ids(self):
        messages={m["type"]:set(m["fields"]) for m in self.contract["messages"]}
        for name in ("PING","STATUS","ASK","ANSWER"):
            self.assertIn("request_id",messages[name])

    def test_nonzero_request_ids(self):
        self.assertEqual(self.contract["request_id_min"], 1)
        self.assertEqual(self.contract["request_id_max"], 4294967295)

    def test_security_defaults(self):
        policy=self.contract["security"]
        self.assertFalse(policy["secrets_on_flipper"])
        self.assertFalse(policy["github_tokens_on_flipper"])
        self.assertTrue(policy["write_operations_require_consent"])

if __name__=="__main__":
    unittest.main()
