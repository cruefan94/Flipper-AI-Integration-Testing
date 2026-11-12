"""Public-only CI checks. No private firmware source or credentials required."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class PublicCiTests(unittest.TestCase):
    def test_public_workspace_discloses_source_boundary(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("not copied here", readme)
        self.assertIn("UNTESTED", readme)

    def test_contract_fixture_roundtrip(self):
        packet = {"version": 1, "id": "smoke-001", "type": "diagnostics.request", "payload": {}}
        decoded = json.loads(json.dumps(packet, separators=(",", ":")))
        self.assertEqual(decoded, packet)
        self.assertIsInstance(decoded["payload"], dict)

    def test_infrastructure_is_not_firmware_validation(self):
        workflow = (ROOT / ".github/workflows/public-ci-smoke.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("runs-on: ubuntu-24.04", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("Flipper-AI-Momentum-.git", workflow)


if __name__ == "__main__":
    unittest.main()
