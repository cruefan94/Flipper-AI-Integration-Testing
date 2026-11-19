"""Synthetic-only non-AI OmniCore SD evidence tests; no firmware or secrets."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

p = Path(__file__).with_name("omnicore_sd_only_gate.py")
spec = importlib.util.spec_from_file_location("omnicore_sd_only_gate", p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
A = "a" * 64
B = "b" * 64


def valid():
    apps = [{"appid": k, "category": category, "path": f"apps/{category}/{k}.fap",
             "bytes": 9999, "sha256": A}
            for k, category in mod.REQUIRED_APPS.items()]
    files = {x["path"]: A for x in apps}
    boards = []
    for chip, asset, folder in (
        ("esp32", "esp32-generic.zip", "ESP32-WROOM32-GhostESP-v221"),
        ("esp32s2", "esp32s2-generic.zip", "ESP32S2-Devboard-GhostESP-v221"),
    ):
        bins = {x: B for x in ("bootloader.bin", "partitions.bin", "firmware.bin")}
        for name in bins:
            files[f"apps_data/esp_flasher/{folder}/{name}"] = B
        boards.append({"chip": chip, "asset": asset, "release_zip_sha256": A,
                       "bootloader_offset": "0x1000", "partitions_offset": "0x8000",
                       "firmware_offset": "0x10000", "bins_sha256": bins,
                       "flipper_flash_approved": False, "device_tested": False})
    files["asset_packs/Demo/Anims/manifest.txt"] = A
    files["infrared/OmniCore_IRDB/Sample.ir"] = A
    return {
        "status": "PRIVATE SD-ONLY PACKAGE; AUTOMATED CHECKS ONLY; NOT HARDWARE TESTED",
        "firmware_included": False, "flash_approved": False, "device_tested": False,
        "momentum_release": "mntm-012", "momentum_sha": mod.MNTM012,
        "asset_pack_count": 49, "asset_pack_folder_count": 53,
        "asset_pack_file_count": 2000, "irdb_profile_count": 5433, "irdb_bytes": 1000000,
        "optional_apps": apps,
        "esp32_firmware": {"release": "v2.2.1", "number_of_boards": 2,
                           "hardware_tested": False,
                           "firmware_flashing_performed": False,
                           "release_asset_sha256_verified": True,
                           "boards": boards},
        "sd_uncompressed_bytes": 5000000,
        "sd_file_count": len(files),
        "sha256": files,
    }


class OmniCoreSdOnlyTests(unittest.TestCase):
    def test_synthetic_success_never_confers_flash_approval(self):
        result = mod.validate(valid())
        self.assertEqual(result["synthetic_metadata_contract"], "PASS")
        self.assertFalse(result["flash_approved"])
        self.assertFalse(result["device_tested"])

    def reject(self, mutator):
        example = deepcopy(valid())
        mutator(example)
        with self.assertRaises(ValueError):
            mod.validate(example)

    def test_missing_fliprpi(self):
        self.reject(lambda v: v["optional_apps"].pop(5))

    def test_missing_esp_flasher(self):
        self.reject(lambda v: v["optional_apps"].pop())

    def test_nine_app_path_integrity(self):
        self.reject(lambda v: v["optional_apps"][-1].update(sha256=B))

    def test_wrong_momentum_sdk(self):
        self.reject(lambda v: v.update(momentum_sha=B))

    def test_missing_ir(self):
        self.reject(lambda v: v.update(irdb_profile_count=5000))

    def test_missing_asset_collection(self):
        self.reject(lambda v: v.update(asset_pack_count=48))

    def test_unverified_esp_release_hash(self):
        self.reject(lambda v: v["esp32_firmware"]["boards"][0].update(release_zip_sha256="unknown"))

    def test_wrong_chip_type(self):
        self.reject(lambda v: v["esp32_firmware"]["boards"][1].update(chip="esp32"))

    def test_esp_firmware_wrong_partition(self):
        self.reject(lambda v: v["esp32_firmware"]["boards"][0].update(firmware_offset="0x30000"))

    def test_mismatched_esp_bin_hash(self):
        self.reject(lambda v: v["esp32_firmware"]["boards"][0]["bins_sha256"].update({"firmware.bin": A}))

    def test_wrong_esp_release_tag(self):
        self.reject(lambda v: v["esp32_firmware"].update(release="rolling"))

    def test_firmware_flashing_not_silent(self):
        self.reject(lambda v: v["esp32_firmware"].update(firmware_flashing_performed=True))

    def test_no_f7_firmware_allowed(self):
        self.reject(lambda v: v.update(firmware_included=True))

    def test_no_flipper_ai(self):
        def bad(v):
            v["sha256"]["apps/GPIO/flipper_ai.fap"] = A
            v["sd_file_count"] += 1
        self.reject(bad)

    def test_missing_real_asset_path(self):
        def bad(v):
            v["sha256"].pop("asset_packs/Demo/Anims/manifest.txt")
            v["sd_file_count"] -= 1
        self.reject(bad)

    def test_disallow_accidental_firmware_updater(self):
        def bad(v):
            v["sha256"]["firmware.dfu"] = A
            v["sd_file_count"] += 1
        self.reject(bad)

    def test_empty_sd_manifest(self):
        self.reject(lambda v: v.update(sha256={}))

    def test_extra_undocumented_app(self):
        self.reject(lambda v: v["optional_apps"].append(v["optional_apps"][0]))

    def test_claimed_hardware_test_rejected(self):
        self.reject(lambda v: v.update(device_tested=True))


if __name__ == "__main__":
    unittest.main()
