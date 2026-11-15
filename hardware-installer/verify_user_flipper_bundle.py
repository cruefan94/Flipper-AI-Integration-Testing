#!/usr/bin/env python3
"""Read-only, standalone verification of a DECRYPTED Flipper AI combined ZIP.

Intended for Python 3 on Android Termux, Raspberry Pi OS, Linux or macOS.
Requires no private source, cloud token, ESP32 or Flipper hardware.
Does NOT decrypt, flash, install an app, or write any device by itself.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile
import zipfile

MAX_ARCHIVE_SIZE = 256 * 1024 * 1024
MAX_MEMBER_SIZE = 128 * 1024 * 1024
MAX_TOTAL_SIZE = 256 * 1024 * 1024
FORMAT = "flipper-ai-esp32-complete-candidate-v1"
REGULAR = {
    "READ_ME_FIRST.txt",
    "SD_CARD/apps/GPIO/esp_flasher.fap",
    "ESP32_WROOM32/firmware.bin",
    "ESP32_WROOM32/bootloader.bin",
    "ESP32_WROOM32/partitions.bin",
    "ESP32_WROOM32/SHA256SUMS.txt",
    "ESP32_WROOM32/READ_FIRST.txt",
    "Licenses/ESP_Flasher_GPL-3.0.txt",
    "Docs/ESP_Flasher_SOURCE_PROVENANCE.txt",
    "Docs/ESP_Flasher_INSTALL_WARNING.txt",
}
HEX40 = re.compile(r"^[a-f0-9]{40}$")
F7_NAME = re.compile(r"^Flipper_Update/(flipper-z-f7-update-[A-Za-z0-9._-]+\.tgz)$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_f7_native(blob: bytes) -> None:
    require(len(blob) <= MAX_MEMBER_SIZE, "Flipper update too large")
    try:
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
            members = archive.getmembers()
            require(0 < len(members) <= 512, "Invalid native F7 member count")
            files = {}
            for m in members:
                path = PurePosixPath(m.name)
                require(not m.issym() and not m.islnk() and (m.isfile() or m.isdir()),
                        "Unsafe F7 archive member")
                require(not m.name.startswith("/") and ".." not in path.parts,
                        "Unsafe native F7 member path")
                require(len(path.parts) in (1, 2) and
                        path.parts[0].startswith("f7-update-"), "Unexpected F7 updater layout")
                if m.isfile():
                    require(len(path.parts) == 2 and m.size <= MAX_MEMBER_SIZE,
                            "Unexpected native firmware file")
                    require(path.parts[1] not in files, "Duplicate native firmware member")
                    if path.parts[1] in ("update.fuf", "firmware.dfu", "updater.bin"):
                        member_file = archive.extractfile(m)
                        require(member_file is not None, "Missing required F7 payload")
                        files[path.parts[1]] = member_file.read(MAX_MEMBER_SIZE + 1)
            require({"update.fuf", "firmware.dfu", "updater.bin"} <= set(files),
                    "Missing native F7 updater components")
            fuf = files["update.fuf"].decode("utf-8", errors="replace")
            require(any(s.strip() == "Target: 7" for s in fuf.splitlines()),
                    "Wrong Flipper hardware target (expected F7)")
            require(any(s.strip() == "Loader: updater.bin" for s in fuf.splitlines()),
                    "Incorrect firmware updater loader")
    except (tarfile.TarError, OSError) as exc:
        raise ValueError("Damaged native firmware archive") from exc


def verify(bundle: Path, expected_source: str | None = None) -> tuple[str, dict]:
    require(bundle.is_file() and not bundle.is_symlink() and
            0 < bundle.stat().st_size < MAX_ARCHIVE_SIZE,
            "Missing, symlinked or oversized decrypted ZIP")
    if expected_source is not None:
        require(bool(HEX40.fullmatch(expected_source)), "Invalid expected source commit")
    try:
        with zipfile.ZipFile(bundle, "r") as z:
            info = z.infolist()
            require(len(info) == len(REGULAR) + 2, "Wrong release file inventory")
            names = [x.filename for x in info]
            require(len(set(names)) == len(names), "Duplicate entries in release ZIP")
            require(sum(x.file_size for x in info) <= MAX_TOTAL_SIZE, "ZIP uncompressed size exceeds limit")
            for member in info:
                path = PurePosixPath(member.filename)
                unix_type = (member.external_attr >> 16) & 0o170000
                require(member.file_size <= MAX_MEMBER_SIZE and not member.is_dir() and
                        not member.filename.startswith("/") and "\\" not in member.filename and
                        ".." not in path.parts and "." not in path.parts and
                        unix_type != 0o120000, "Unsafe ZIP member")
            flipper = [n for n in names if F7_NAME.fullmatch(n)]
            require(len(flipper) == 1 and set(names) ==
                    REGULAR | {"MANIFEST.json", flipper[0]}, "Unexpected release inventory")
            require(z.testzip() is None, "ZIP integrity test failed")
            manifest = json.loads(z.read("MANIFEST.json"))
            require(manifest.get("format") == FORMAT and manifest.get("auto_flash") is False and
                    manifest.get("hardware_verified") is False,
                    "Not an explicitly untested, manual-flash Flipper AI release")
            require("Flipper Zero F7" in manifest.get("target", "") and
                    "ESP-WROOM-32" in manifest.get("target", ""),
                    "Wrong firmware hardware target")
            source = manifest.get("flipper_source_revision")
            require(isinstance(source, str) and bool(HEX40.fullmatch(source)),
                    "Invalid private firmware source revision")
            require(manifest.get("esp32_source_revision") == source,
                    "Flipper/ESP32 firmware source revisions differ")
            for key in ("momentum_sdk_revision", "flasher_upstream_revision", "flasher_patch_revision"):
                value = manifest.get(key)
                require(isinstance(value, str) and bool(HEX40.fullmatch(value)),
                        "Invalid or missing pinned build revision: " + key)
            if expected_source is not None:
                require(source == expected_source, "Candidate does not match expected private source commit")
            records = manifest.get("files")
            require(isinstance(records, dict) and set(records) == set(names) - {"MANIFEST.json"},
                    "Manifest inventory mismatch")
            for name, record in records.items():
                require(isinstance(record, dict) and
                        record.get("size") == z.getinfo(name).file_size and
                        record.get("sha256") == hashlib.sha256(z.read(name)).hexdigest(),
                        "SHA256 or size mismatch: " + name)
            verify_f7_native(z.read(flipper[0]))
            require(z.read("SD_CARD/apps/GPIO/esp_flasher.fap").startswith(b"\x7fELF"),
                    "Missing compiled ESP programmer FAP")
            require(z.read("ESP32_WROOM32/firmware.bin").startswith(b"\xe9"),
                    "Invalid classic ESP32 firmware header")
            require(z.read("ESP32_WROOM32/bootloader.bin").startswith(b"\xe9"),
                    "Invalid classic ESP32 bootloader header")
            require(b"GNU GENERAL PUBLIC LICENSE" in
                    z.read("Licenses/ESP_Flasher_GPL-3.0.txt").upper(),
                    "Missing GPL license file")
            require(b"NOT" in z.read("READ_ME_FIRST.txt").upper(),
                    "Missing untested-flash safety notice")
            return flipper[0], manifest
    except (zipfile.BadZipFile, OSError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid, incomplete or corrupted decrypted ZIP") from exc


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("bundle", type=Path, help="Decrypted FlipperAI_ESP32_Complete_Flash_Candidate_UNTESTED.zip")
    p.add_argument("--expect-source", help="Exact expected 40-character private firmware commit")
    p.add_argument("--extract-flipper", type=Path,
                   help="Optional directory for extracting ONLY the validated Flipper .tgz; never flashes")
    args = p.parse_args()
    try:
        native, manifest = verify(args.bundle, args.expect_source)
        print("VERIFIED: exact Flipper F7 updater, contents SHA256, source pins and safety manifest")
        print("Flipper source revision:", manifest["flipper_source_revision"])
        print("Native F7 updater:", Path(native).name)
        print("HARDWARE: UNTESTED; installer and ESP32 flashing are NOT performed")
        if args.extract_flipper is not None:
            folder = args.extract_flipper
            require(not folder.is_symlink(), "Refusing symlink destination")
            folder.mkdir(parents=True, exist_ok=True)
            target = folder / Path(native).name
            require(not target.exists() and not target.is_symlink(),
                    "Refusing to overwrite an existing firmware updater")
            with zipfile.ZipFile(args.bundle) as z:
                # O_EXCL avoids overwriting if another process creates this file.
                fd = os.open(str(target), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                try:
                    with os.fdopen(fd, "wb") as dest, z.open(native) as src:
                        while True:
                            chunk = src.read(1024 * 1024)
                            if not chunk:
                                break
                            dest.write(chunk)
                except BaseException:
                    target.unlink(missing_ok=True)
                    raise
            print("Verified native .tgz extracted (NOT flashed):", target)
    except ValueError as exc:
        p.exit(2, "VERIFICATION FAILED: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
