import io
import unittest
from urllib.error import HTTPError
from unittest.mock import patch
from scripts.ai_dev_gateway import Gateway, GatewayError

class ProviderDiagnosticsTests(unittest.TestCase):
    def test_http_error_reports_status_without_body(self):
        err = HTTPError("https://example.org", 429, "rate limit", {}, io.BytesIO(b"secret-provider-body"))
        with patch("scripts.ai_dev_gateway.request.urlopen", side_effect=err):
            with self.assertRaises(GatewayError) as caught:
                Gateway._post("https://example.org", {}, {"messages": []}, 5)
        self.assertIn("429", str(caught.exception))
        self.assertNotIn("secret-provider-body", str(caught.exception))

if __name__ == "__main__":
    unittest.main()
