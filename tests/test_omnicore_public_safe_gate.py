"""Offline tests with invented metadata only; NEVER import private firmwares."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import unittest

SOURCE = Path(__file__).with_name("omnicore_public_safe_gate.py")
spec = importlib.util.spec_from_file_location("omnicore_public_safe_gate", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
APPS = set(mod.REQUIRED_APPS)
SHA = "a" * 64
SOURCE_SHA = "b" * 64


def valid_records():
    apps = {name: {"path": f"apps/GPIO/{name}.fap",
                   "sha256": SHA, "bytes": 4096} for name in APPS}
    staged = {name: {"revision": SOURCE_SHA, "repo": "example/open-source"}
              for name in APPS}
    build = {"source_sha": SOURCE_SHA, "sha256": SHA, "size": 4096000,
             "status": "PRIVATE UNTESTED; NOT FLASH APPROVED",
             "resources_verified": True, "complete_resources_verified": True,
             "resource_file_count": 1100, "installed_fap_count": 100}
    embedded = {"updater_sha256": SHA, "first_flash_preload_integrity_verified": True,
                "device_tested": False, "flash_approved": False,
                "embedded_asset_pack_choices": 48, "embedded_ir_profiles": 10,
                "embedded_optional_apps": apps}
    resource = {"full_native_resource_tree_match": True, "flash_approved": False,
                "device_tested": False, "missing_resources": 0,
                "extra_resources": 0, "hash_mismatches": 0,
                "files_byte_for_byte_verified": 1100,
                "compiled_faps_including_original_momentum": 100}
    preload = {"asset_choices": 48, "device_tested": False,
               "flash_approved": False, "apps": staged}
    return build, embedded, resource, preload


class OmniCorePublicSafeGateTest(unittest.TestCase):
    def test_valid_synthetic_reports_pass_but_not_flash_approved(self):
        report = mod.validate(*valid_records())
        self.assertEqual(report["metadata_gate"], "passed")
        self.assertFalse(report["flash_approved"])
        self.assertFalse(report["real_hardware_tested"])
        self.assertFalse(report["public_release_allowed"])

    def check_reject(self, changed):
        records = list(deepcopy(valid_records()))
        changed(records)
        with self.assertRaises(ValueError):
            mod.validate(*records)

    def test_missing_fliprpi_rejected(self):
        self.check_reject(lambda xs: xs[1]["embedded_optional_apps"].pop("flip_rpi"))

    def test_missing_unitemp_rejected(self):
        self.check_reject(lambda xs: xs[3]["apps"].pop("unitemp"))

    def test_missing_i2c_tools_rejected(self):
        self.check_reject(lambda xs: xs[1]["embedded_optional_apps"].pop("i2c_tools_cli"))

    def test_fap_bad_digest_rejected(self):
        self.check_reject(lambda xs: xs[1]["embedded_optional_apps"]["flip_rpi"].update(sha256="xyz"))

    def test_ai_app_rejected(self):
        self.check_reject(lambda xs: xs[3]["apps"].update(flipper_ai={"revision": SHA}))

    def test_missing_resources_rejected(self):
        self.check_reject(lambda xs: xs[2].update(missing_resources=1))

    def test_mismatched_resources_rejected(self):
        self.check_reject(lambda xs: xs[2].update(hash_mismatches=1))

    def test_wrong_updater_sha_rejected(self):
        self.check_reject(lambda xs: xs[1].update(updater_sha256=SOURCE_SHA))

    def test_missing_source_pin_rejected(self):
        self.check_reject(lambda xs: xs[3]["apps"]["flip_rpi"].update(revision="latest"))

    def test_fake_hardware_test_rejected(self):
        self.check_reject(lambda xs: xs[1].update(device_tested=True))

    def test_claimed_flash_approval_rejected(self):
        self.check_reject(lambda xs: xs[0].update(status="FLASH APPROVED"))

    def test_incomplete_original_native_resources_rejected(self):
        self.check_reject(lambda xs: xs[0].update(resource_file_count=999))

    def test_skipped_native_f7_compiler_rejected(self):
        self.check_reject(lambda xs: xs[0].update(resources_verified=False))


if __name__ == "__main__":
    unittest.main()
