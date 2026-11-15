#!/usr/bin/env python3
"""Compose one opt-in Flipper AI ESP32 flash-release candidate.

Takes three ALREADY VERIFIED plaintext development packages on an ephemeral
private build runner, checks source/SDK pairings, and generates a hash-verified
ZIP for PASSPHRASE ENCRYPTION. Never uploads plaintext, performs a flash,
writes a Flipper SD card or auto-installs the external GPL application.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import zipfile

import prepare_momentum_flash_package as f7
import prepare_esp_flasher_delivery as programmer

VERSION = "flipper-ai-esp32-complete-candidate-v1"
BUNDLE_NAME = "FlipperAI_ESP32_Complete_Flash_Candidate_UNTESTED.zip"
MAX_WROOM_ARCHIVE = 12 * 1024 * 1024
WROOM_MEMBERS = {
    "firmware.bin", "bootloader.bin", "partitions.bin",
    "READ_FIRST.txt", "SHA256SUMS.txt"
}
HEX40 = re.compile(r"^[a-f0-9]{40}$")
HEX64 = re.compile(r"^[a-f0-9]{64}$")


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _tar_files(path: Path, limit: int, expected: set[str]) -> dict[str, bytes]:
    if not path.is_file() or path.is_symlink() or not 0 < path.stat().st_size <= limit:
        raise ValueError("Missing, linked, empty or oversized input archive")
    content = {}
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        if len(members) != len(expected):
            raise ValueError("Unexpected archive member count")
        for member in members:
            if (not member.isfile() or member.name not in expected
                    or member.name in content or member.size > limit):
                raise ValueError("Unsafe or unexpected archive entry")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("Unreadable archive member")
            content[member.name] = stream.read(limit + 1)
            if len(content[member.name]) != member.size:
                raise ValueError("Archive entry size mismatch")
    if set(content) != expected:
        raise ValueError("Archive inventory mismatch")
    return content


def _wroom_package(path: Path) -> tuple[dict[str, bytes], str]:
    content = _tar_files(path, MAX_WROOM_ARCHIVE, WROOM_MEMBERS)
    hashes = {}
    for line in content["SHA256SUMS.txt"].decode("ascii").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if not match or match.group(2) in hashes:
            raise ValueError("Malformed or duplicate ESP32 SHA256")
        hashes[match.group(2)] = match.group(1)
    if set(hashes) != WROOM_MEMBERS - {"SHA256SUMS.txt"}:
        raise ValueError("ESP32 SHA256 inventory mismatch")
    for name, expected in hashes.items():
        if sha(content[name]) != expected:
            raise ValueError("ESP32 image SHA256 mismatch")
    for name in ("firmware.bin", "bootloader.bin"):
        blob = content[name]
        if len(blob) < 32 or blob[0] != 0xE9:
            raise ValueError("Missing classic ESP32 firmware image header")
    if not 0 < len(content["partitions.bin"]) <= 32768:
        raise ValueError("Invalid ESP32 partition table size")
    readme = content["READ_FIRST.txt"].decode("ascii")
    if ("BOARD_TARGET=esp32dev" not in readme or
            "Not for ESP32-S2" not in readme or
            "Not for ESP32-S2, Arduino Uno" not in readme or
            "no automatic board flash" not in readme.lower()):
        raise ValueError("ESP32 safety/target warning missing")
    match = re.search(r"^SOURCE_REVISION=([0-9a-f]{40})$", readme, re.MULTILINE)
    if not match:
        raise ValueError("ESP32 source revision not pinned")
    return content, match.group(1)


def _read_f7(path: Path) -> tuple[dict, str, bytes]:
    name = f7.verify_package(path)
    with tarfile.open(path, "r:gz") as tar:
        manifest = json.load(tar.extractfile(f7.MANIFEST))
        blob = tar.extractfile(name).read(f7.MAX_TGZ_BYTES + 1)
    return manifest, name, blob


def build(firmware: Path, flasher: Path, esp32: Path, output: Path) -> Path:
    firmware_manifest, native_name, native_blob = _read_f7(firmware)
    flasher_manifest = programmer.verify(flasher)
    flasher_files = programmer._read_package(flasher)
    esp_files, esp_source = _wroom_package(esp32)
    source = firmware_manifest["source_revision"]
    sdk = firmware_manifest["momentum_revision"]
    if not HEX40.fullmatch(source) or not HEX40.fullmatch(sdk):
        raise ValueError("Private firmware or Momentum SDK source is unpinned")
    if (flasher_manifest["firmware_source_revision"] != source or
            flasher_manifest["momentum_revision"] != sdk or
            esp_source != source):
        raise ValueError("Firmware, programmer and ESP32 image revisions do not match")
    if output.exists() or output.is_symlink():
        raise ValueError("Refusing overwrite of release candidate")
    payload = {
        "Flipper_Update/" + native_name: native_blob,
        "SD_CARD/apps/GPIO/esp_flasher.fap": flasher_files["esp_flasher.fap"],
        "ESP32_WROOM32/firmware.bin": esp_files["firmware.bin"],
        "ESP32_WROOM32/bootloader.bin": esp_files["bootloader.bin"],
        "ESP32_WROOM32/partitions.bin": esp_files["partitions.bin"],
        "ESP32_WROOM32/SHA256SUMS.txt": esp_files["SHA256SUMS.txt"],
        "ESP32_WROOM32/READ_FIRST.txt": esp_files["READ_FIRST.txt"],
        "Licenses/ESP_Flasher_GPL-3.0.txt": flasher_files["LICENSE_GPL-3.0.txt"],
        "Docs/ESP_Flasher_SOURCE_PROVENANCE.txt": flasher_files["SOURCE_PROVENANCE.txt"],
        "Docs/ESP_Flasher_INSTALL_WARNING.txt": flasher_files["READ_ME_BEFORE_INSTALL.txt"],
    }
    readme = (
        "FLIPPER AI + ESP32 COMPONENT COMPATIBILITY - UNTESTED RELEASE CANDIDATE\n\n"
        "This is NOT one flashable image. Different chips require separate firmware.\n"
        "Step 1: Verify device and retain a known-good Momentum/qFlipper recovery image.\n"
        "Step 2: Flipper_Update/*.tgz is ONLY for a compatible Flipper Zero F7 firmware updater.\n"
        "Step 3: SD_CARD/apps/GPIO/esp_flasher.fap is a separate GPL ESP programmer app,\n"
        "        compiled against the matching custom Momentum SDK. Installing it on SD\n"
        "        does NOT initiate a flash. Preserve its GPL license and source provenance.\n"
        "Step 4: ESP32_WROOM32/ contains reference firmware for CLASSIC ESP-WROOM-32 only.\n"
        "        Its images are NOT for ESP32-S2 or Arduino Uno. DO NOT flash the\n"
        "        ESP32 until chip identity, flash size, partitions, offsets, power\n"
        "        routing, USB-UART contention and BOOT/EN behavior are verified.\n"
        "        Every erase/write must be approved directly on the Flipper.\n"
        "Step 5: ESP32 sensor menus require a physically connected and flashed board;\n"
        "        they do NOT detect every Arduino sensor or program Arduino Uno sketches.\n"
        "The custom internal ESP32 Manager and Flipper AI have exclusive UART ownership.\n"
        "Exit one before launching the other. No automatic ESP32 flashing is implemented.\n"
        "CAUTION: UNO 5V GPIO must never directly touch Flipper/ESP32 3.3V pins.\n"
        "No physical flash or sensor tests have been performed. DO NOT install blindly.\n"
    ).encode("ascii")
    payload["READ_ME_FIRST.txt"] = readme
    manifest = {
        "format": VERSION,
        "target": "Flipper Zero F7 / classic ESP-WROOM-32 (separate devices)",
        "hardware_verified": False,
        "auto_flash": False,
        "flipper_source_revision": source,
        "momentum_sdk_revision": sdk,
        "esp32_source_revision": esp_source,
        "flasher_upstream_revision": flasher_manifest["upstream_revision"],
        "flasher_patch_revision": flasher_manifest["patch_revision"],
        "files": {name: {"sha256": sha(blob), "size": len(blob)}
                  for name, blob in sorted(payload.items())},
    }
    payload["MANIFEST.json"] = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as z:
        for name, blob in sorted(payload.items()):
            z.writestr(name, blob)
    try:
        verify(output)
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return output


def verify(path: Path) -> dict:
    if not path.is_file() or path.is_symlink() or not 0 < path.stat().st_size < 256 * 1024 * 1024:
        raise ValueError("Invalid unified release candidate path/size")
    with zipfile.ZipFile(path) as z:
        info = z.infolist()
        names = [m.filename for m in info]
        if len(names) < 10 or len(names) != len(set(names)) or "MANIFEST.json" not in names:
            raise ValueError("Missing, duplicated or oversized release inventory")
        if z.testzip() is not None:
            raise ValueError("Damaged ZIP member")
        for m in info:
            p = PurePosixPath(m.filename)
            if (m.is_dir() or m.filename.startswith("/") or
                    "\\" in m.filename or ".." in p.parts or
                    "." in p.parts or m.file_size > 128 * 1024 * 1024 or
                    (m.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError("Unsafe ZIP entry")
        manifest = json.loads(z.read("MANIFEST.json"))
        if (manifest.get("format") != VERSION or manifest.get("auto_flash") is not False
                or manifest.get("hardware_verified") is not False):
            raise ValueError("Wrong release version or unsafe automatic-flash status")
        entries = manifest["files"]
        if set(entries) != set(names) - {"MANIFEST.json"}:
            raise ValueError("Manifest inventory mismatch")
        for name, record in entries.items():
            if record.get("size") != z.getinfo(name).file_size or sha(z.read(name)) != record.get("sha256"):
                raise ValueError("Mismatch in release entry: " + name)
        if sum(name.startswith("Flipper_Update/") for name in entries) != 1:
            raise ValueError("Expected exactly one native Flipper update")
        if not z.read("SD_CARD/apps/GPIO/esp_flasher.fap").startswith(b"\x7fELF"):
            raise ValueError("Missing actual compiled FAP")
        if b"GNU GENERAL PUBLIC LICENSE" not in z.read("Licenses/ESP_Flasher_GPL-3.0.txt").upper():
            raise ValueError("GPL compliance notice missing")
        if b"NOT" not in z.read("READ_ME_FIRST.txt"):
            raise ValueError("Safety warning missing")
        for field in ("flipper_source_revision", "momentum_sdk_revision", "esp32_source_revision",
                      "flasher_upstream_revision", "flasher_patch_revision"):
            if not isinstance(manifest.get(field), str) or not HEX40.fullmatch(manifest[field]):
                raise ValueError("Unpinned release revision")
        if manifest["flipper_source_revision"] != manifest["esp32_source_revision"]:
            raise ValueError("Paired device software revisions differ")
        return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    subs = ap.add_subparsers(dest="mode", required=True)
    build_cmd = subs.add_parser("pack")
    build_cmd.add_argument("--firmware", type=Path, required=True)
    build_cmd.add_argument("--flasher", type=Path, required=True)
    build_cmd.add_argument("--esp32", type=Path, required=True)
    build_cmd.add_argument("--out", type=Path, required=True)
    check = subs.add_parser("verify")
    check.add_argument("--archive", type=Path, required=True)
    args = ap.parse_args()
    if args.mode == "pack":
        print("Verified unified release candidate:", build(args.firmware, args.flasher, args.esp32, args.out))
    else:
        info = verify(args.archive)
        print("Verified unified bundle:", info["flipper_source_revision"])


if __name__ == "__main__":
    main()
