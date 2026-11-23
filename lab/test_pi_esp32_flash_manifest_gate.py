"""Public-safe synthetic tests: no serial access or firmware bytes."""
import importlib.util
import pathlib
import unittest

path = pathlib.Path(__file__).with_name("pi_esp32_flash_manifest_gate.py")
spec = importlib.util.spec_from_file_location("manifest_gate", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def good():
    return dict(board="esp32-wroom-32", board_identity_verified=True,
                transport="usb_serial", image_sha256="a"*64,
                image_bytes=1024, owner_approved=True)

class GateTests(unittest.TestCase):
    def test_complete_metadata_still_never_authorizes_flash(self):
        r = module.inspect_manifest(good())
        self.assertTrue(r["valid_metadata"])
        self.assertFalse(r["flash_authorized"])

    def test_rejects_missing_approval(self):
        d = good(); d["owner_approved"] = False
        self.assertIn("owner_approval", module.inspect_manifest(d)["errors"])

    def test_rejects_unverified_board(self):
        d = good(); d["board_identity_verified"] = False
        self.assertIn("board_identity", module.inspect_manifest(d)["errors"])

    def test_rejects_wrong_transport(self):
        d = good(); d["transport"] = "wifi"
        self.assertIn("transport", module.inspect_manifest(d)["errors"])

    def test_rejects_bad_digest(self):
        d = good(); d["image_sha256"] = "a"*63 + "G"
        self.assertIn("sha256_format", module.inspect_manifest(d)["errors"])

    def test_rejects_bool_as_size(self):
        d = good(); d["image_bytes"] = True
        self.assertIn("image_size", module.inspect_manifest(d)["errors"])

    def test_rejects_extra_fields(self):
        d = good(); d["serial_number"] = "sensitive"
        self.assertEqual(module.inspect_manifest(d)["errors"], ["schema"])

    def test_rejects_non_dict(self):
        self.assertEqual(module.inspect_manifest([])["errors"], ["schema"])

    def test_s2_is_separate_explicit_board(self):
        d = good(); d["board"] = "esp32-s2-devboard"
        self.assertTrue(module.inspect_manifest(d)["valid_metadata"])

if __name__ == "__main__":
    unittest.main()
