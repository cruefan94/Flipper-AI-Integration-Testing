#!/usr/bin/env python3
"""Public-safe synthetic metadata gate for private NON-AI OmniCore SD-only builds.

Never accept/upload firmware bytes or a real private evidence file in public
CI. Run this exact source as a local parser in the private GitHub runner.
A pass validates metadata shape and internal consistency only, not hardware.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

MNTM012 = "e1784e7418d8b074e971983ceb6fef0f37e52ae4"
REQUIRED_APPS = {
    "tag_ident": "NFC",
    "nfc_convert": "NFC",
    "nfc_compare": "NFC",
    "rfsurvey": "Sub-GHz",
    "hermes": "GPIO",
    "flip_rpi": "GPIO",
    "unitemp": "GPIO",
    "i2c_tools_cli": "GPIO",
    "esp_flasher": "GPIO",
}
SHA = re.compile(r"[0-9a-f]{64}\Z")
EXPECTED_CHIPS = {"esp32", "esp32s2"}
EXPECTED_ASSETS = {"esp32-generic.zip", "esp32s2-generic.zip"}


def require(value: bool, why: str) -> None:
    if not value:
        raise ValueError(why)


def valid_digest(s: object) -> bool:
    return isinstance(s, str) and bool(SHA.fullmatch(s))


def validate(data: dict) -> dict:
    require(isinstance(data, dict), "Evidence must be a dictionary")
    require(data.get("firmware_included") is False
            and data.get("flash_approved") is False
            and data.get("device_tested") is False,
            "Firmware/hardware safe-hold missing")
    require(data.get("momentum_release") == "mntm-012"
            and data.get("momentum_sha") == MNTM012,
            "Wrong installed Momentum SDK baseline")
    require(data.get("asset_pack_count") == 49
            and data.get("asset_pack_folder_count") >= 53
            and data.get("asset_pack_file_count", 0) > 200,
            "Missing assets/animations/fonts")
    require(data.get("irdb_profile_count") == 5433
            and data.get("irdb_bytes", 0) > 1000,
            "Incomplete original public IR catalog")
    apps = data.get("optional_apps")
    require(isinstance(apps, list) and len(apps) == len(REQUIRED_APPS),
            "Missing or duplicate optional apps")
    app_map = {}
    for item in apps:
        require(isinstance(item, dict) and isinstance(item.get("appid"), str),
                "Malformed app record")
        name = item["appid"]
        require(name not in app_map and name in REQUIRED_APPS,
                "Unknown or duplicate app ID")
        require(item.get("category") == REQUIRED_APPS[name]
                and item.get("path") == f"apps/{REQUIRED_APPS[name]}/{name}.fap"
                and item.get("bytes", 0) >= 100
                and valid_digest(item.get("sha256")),
                "App compiled-path/checksum record invalid")
        app_map[name] = item
    require(set(app_map) == set(REQUIRED_APPS), "Not all required apps present")
    require("flipper_ai" not in app_map, "Flipper AI must be absent")

    esp = data.get("esp32_firmware")
    require(isinstance(esp, dict)
            and esp.get("number_of_boards") == 2
            and esp.get("release") == "v2.2.1"
            and esp.get("hardware_tested") is False
            and esp.get("firmware_flashing_performed") is False
            and esp.get("release_asset_sha256_verified") is True,
            "No independently checked two-board ESP payload")
    boards = esp.get("boards")
    require(isinstance(boards, list) and len(boards) == 2,
            "Two distinct ESP32 chip manifests mandatory")
    chips = set()
    assets = set()
    for board in boards:
        require(isinstance(board, dict), "Malformed ESP image evidence")
        chips.add(board.get("chip"))
        assets.add(board.get("asset"))
        require(board.get("flipper_flash_approved") is False
                and board.get("device_tested") is False
                and valid_digest(board.get("release_zip_sha256"))
                and board.get("bootloader_offset") == "0x1000"
                and board.get("partitions_offset") == "0x8000"
                and board.get("firmware_offset") in ("0x10000", "0x20000"),
                "Unsafe/missing chip-offset release metadata")
        bins = board.get("bins_sha256")
        require(isinstance(bins, dict)
                and set(bins) == {"bootloader.bin", "partitions.bin", "firmware.bin"}
                and all(valid_digest(x) for x in bins.values()),
                "Unverified original ESP binary hashes")
    require(chips == EXPECTED_CHIPS and assets == EXPECTED_ASSETS,
            "Generic WROOM and ESP32-S2 board types are not distinct")

    files = data.get("sha256")
    require(isinstance(files, dict) and all(valid_digest(x) for x in files.values()),
            "Per-file SHA256 report absent or malformed")
    require(any(str(x).startswith("asset_packs/") for x in files)
            and any(str(x).startswith("infrared/OmniCore_IRDB/") for x in files),
            "Required asset packs and IR paths not in SD evidence")
    require(not any(str(x).endswith((".dfu", ".tgz", ".fuf")) for x in files),
            "Updater firmware accidentally included in SD resources")
    require(data.get("sd_file_count") == len(files)
            and data.get("sd_uncompressed_bytes", 0) > 100_000
            and all(not str(x).startswith("flipper_ai/") for x in files)
            and not any("flipper_ai" in str(x).lower() for x in files),
            "Incomplete SD file evidence or AI app present")
    expected_files = {app["path"] for app in apps}
    for board in boards:
        folder = ("ESP32-WROOM32-GhostESP-v221" if board["chip"] == "esp32"
                  else "ESP32S2-Devboard-GhostESP-v221")
        expected_files.update(
            f"apps_data/esp_flasher/{folder}/{file_name}"
            for file_name in ("bootloader.bin", "partitions.bin", "firmware.bin"))
    require(expected_files.issubset(files), "Missing compiled app or ESP image in SD tree")
    for app in apps:
        require(files[app["path"]] == app["sha256"],
                "Compiled app digest and packaged SD digest differ")
    for board in boards:
        folder = ("ESP32-WROOM32-GhostESP-v221" if board["chip"] == "esp32"
                  else "ESP32S2-Devboard-GhostESP-v221")
        for name, digest in board["bins_sha256"].items():
            require(files[f"apps_data/esp_flasher/{folder}/{name}"] == digest,
                    "ESP binary hash and packaged SD digest differ")
    return {
        "synthetic_metadata_contract": "PASS",
        "private_release_verified": False,
        "device_tested": False,
        "flash_approved": False,
        "no_flipper_ai": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-evidence-json", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = validate(json.loads(args.private_evidence_json.read_text(encoding="utf-8")))
    except (ValueError, TypeError, KeyError):
        raise SystemExit("FAIL: private OmniCore SD metadata consistency (no private data printed)")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
