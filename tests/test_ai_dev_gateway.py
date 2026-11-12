import os
import unittest
from unittest.mock import patch
from scripts.ai_dev_gateway import Gateway, GatewayError

CONFIG = {"default_provider": "mock", "providers": {
    "mock": {"kind": "mock"},
    "external": {"kind": "openai_compatible", "endpoint": "https://example.org/v1/chat/completions",
                 "model": "test", "api_key_env": "FLIPPER_AI_TEST_KEY"},
    "local": {"kind": "openai_compatible", "endpoint": "http://127.0.0.1:8080/v1/chat/completions",
              "model": "local", "requires_api_key": False, "allow_http_local": True},
}}

class GatewayTests(unittest.TestCase):
    def test_default_offline(self):
        self.assertTrue(Gateway(CONFIG).ask("help")["simulated"])

    def test_invalid_prompt(self):
        with self.assertRaises(GatewayError):
            Gateway(CONFIG).ask("")

    def test_network_opt_in(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(GatewayError):
            Gateway(CONFIG).ask("hello", "external")

    def test_external_switch(self):
        seen = []
        def fake(url, headers, payload, timeout):
            seen.append((url, headers, payload))
            return {"choices": [{"message": {"content": "ready"}}]}
        with patch.dict(os.environ, {"FLIPPER_AI_DEV_NETWORK": "1", "FLIPPER_AI_TEST_KEY": "test-secret"}):
            result = Gateway(CONFIG, fake).ask("hello", "external")
        self.assertEqual(result["answer"], "ready")
        self.assertEqual(seen[0][2]["messages"][0]["content"], "hello")
        self.assertEqual(seen[0][1]["Authorization"], "Bearer test-secret")

    def test_local_switch(self):
        with patch.dict(os.environ, {"FLIPPER_AI_DEV_NETWORK": "1"}, clear=True):
            result = Gateway(CONFIG, lambda *args: {"choices": [{"message": {"content": "local reply"}}]}).ask("hi", "local")
        self.assertEqual(result["answer"], "local reply")

    def test_nonlocal_plain_http_rejected(self):
        config = {"providers": {"bad": {"kind": "openai_compatible", "endpoint": "http://example.org/api",
                                        "model": "x", "requires_api_key": False, "allow_http_local": True}}}
        with patch.dict(os.environ, {"FLIPPER_AI_DEV_NETWORK": "1"}), self.assertRaises(GatewayError):
            Gateway(config, lambda *args: None).ask("hi", "bad")

if __name__ == "__main__":
    unittest.main()
