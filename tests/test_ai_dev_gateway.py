import unittest
from scripts.ai_dev_gateway import ManualProvider, OpenAICompatibleProvider, select_provider, run_task

class GatewayTests(unittest.TestCase):
    def test_default_offline_and_no_credentials(self):
        self.assertIsInstance(select_provider({}), ManualProvider)
        self.assertIn("not configured", run_task("Review protocol", {}))

    def test_requires_explicit_opt_in(self):
        self.assertIsInstance(select_provider({"FLIPPER_DEV_AI_ENDPOINT": "https://example.com/v1/chat/completions"}), ManualProvider)

    def test_https_required(self):
        with self.assertRaises(ValueError):
            OpenAICompatibleProvider("http://example.com/v1/chat/completions", "model", "key")

    def test_credentials_must_not_be_embedded_in_url(self):
        with self.assertRaises(ValueError):
            OpenAICompatibleProvider("https://user:pass@example.com/v1/chat/completions", "model", "key")

    def test_future_local_model_compatible(self):
        class OwnModel:
            def complete(self, prompt):
                return "local:" + prompt
        provider = OwnModel()
        self.assertEqual(provider.complete("build"), "local:build")

    def test_empty_task_rejected(self):
        with self.assertRaises(ValueError):
            run_task(" ", {})

if __name__ == "__main__":
    unittest.main()
