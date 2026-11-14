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

    def test_private_source_and_credentials_not_published(self):
        # Public CI must remain a contract-only project, never a firmware mirror.
        forbidden_dirs = ("flipper_app", "esp32s2", "cloudflare_worker", "momentum")
        for name in forbidden_dirs:
            self.assertFalse((ROOT / name).exists(), f"Private project directory leaked: {name}")
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            self.assertNotIn(path.name.lower(), (".env", "id_rsa", "id_ed25519"))
            self.assertFalse(path.suffix.lower() in (".pem", ".p12", ".pfx", ".key"),
                             f"Possible private key committed: {path.relative_to(ROOT)}")

    def test_infrastructure_is_not_firmware_validation(self):
        workflow = (ROOT / ".github/workflows/public-ci-smoke.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("runs-on: ubuntu-24.04", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("Flipper-AI-Momentum-.git", workflow)


if __name__ == "__main__":
    unittest.main()
