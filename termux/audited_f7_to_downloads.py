#!/usr/bin/env python3
"""Verify and extract ONE pinned, audited F7 firmware ZIP from local Android Downloads.

This program NEVER flashes a device, never changes an ESP32, and does not upload
a passphrase. It expects the signed-in owner to download Actions artifact
14189530383 from successful workflow run 43782149547 using their browser.
The downloaded outer ZIP is checked against GitHub's published SHA-256 digest.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

# This public helper contains the previously regression-tested native TGZ
# manifest and complete F7 firmware file hash verification.
from firmware_to_phone import (
    DeliveryError, decrypt_and_verify_artifact, sha256,
)

RUN_ID = 43782149547
ARTIFACT_ID = 14189530383
ARTIFACT_STEM = "encrypted-flipper-ai-esp32-integration-preview-tgz-UNTESTED"
ARTIFACT_DIGEST = "e7990b391a3959de297fd3df64cebe5ba070de74556cc9f1ad5539bbd80d0718"
ENCRYPTED_NAME = "flipper-ai-native-tgz-delivery.tar.gz.enc"
SOURCE_REVISION = "642e267612f1c555c60eb0db2ec167f5d2ab036f"
MAX_ARCHIVE_BYTES = 100 * 1024 * 1024


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def identify_input(file_or_directory: Path | None, downloads: Path) -> Path:
    if file_or_directory is not None:
        chosen = file_or_directory.expanduser()
        if not chosen.is_file() or chosen.is_symlink():
            raise DeliveryError("Selected artifact is not a regular file")
        return chosen
    # Prefer the original GitHub artifact ZIP. Do not accidentally pick the
    # similarly named combined release ZIP or an older package.
    locations = [downloads, Path.home() / "downloads"]
    zip_candidates = []
    enc_candidates = []
    for folder in locations:
        if not folder.is_dir():
            continue
        zip_candidates.extend(x for x in folder.glob("**/" + ARTIFACT_STEM + ".zip")
                              if x.is_file() and not x.is_symlink())
        enc_candidates.extend(x for x in folder.glob("**/" + ENCRYPTED_NAME)
                              if x.is_file() and not x.is_symlink())
    unique_zip = {str(x.resolve()): x for x in zip_candidates}
    unique_enc = {str(x.resolve()): x for x in enc_candidates}
    if len(unique_zip) == 1:
        return next(iter(unique_zip.values()))
    if len(unique_zip) > 1:
        raise DeliveryError("Multiple firmware artifact ZIPs found; pass --input with the exact file")
    if len(unique_enc) == 1:
        return next(iter(unique_enc.values()))
    if len(unique_enc) > 1:
        raise DeliveryError("Multiple encrypted firmware files found; pass --input with the exact file")
    raise DeliveryError(
        "Audited firmware not found in Downloads. Get GitHub Actions run "
        f"{RUN_ID} artifact {ARTIFACT_STEM} (not the ESP32 combined ZIP).")


def extract_encrypted_from_outer_zip(outer: Path, destination: Path,
                                     expected_digest: str = ARTIFACT_DIGEST) -> Path:
    if not outer.is_file() or outer.is_symlink():
        raise DeliveryError("Expected a regular GitHub artifact ZIP")
    if outer.stat().st_size > MAX_ARCHIVE_BYTES:
        raise DeliveryError("GitHub artifact ZIP exceeds size limit")
    if file_digest(outer) != expected_digest:
        raise DeliveryError(
            "GitHub Actions artifact ZIP SHA-256 mismatch. It may be the wrong "
            "build or a damaged download. Do not decrypt/flash it.")
    try:
        with zipfile.ZipFile(outer) as z:
            members = z.infolist()
            if len(members) != 1 or members[0].filename != ENCRYPTED_NAME:
                raise DeliveryError("Wrong artifact contents; expected only the encrypted native F7 delivery")
            info = members[0]
            mode = (info.external_attr >> 16) & 0o170000
            if info.is_dir() or mode == 0o120000 or info.file_size > MAX_ARCHIVE_BYTES:
                raise DeliveryError("Unsafe entry inside artifact ZIP")
            if z.testzip() is not None:
                raise DeliveryError("Damaged GitHub artifact ZIP CRC")
            path = destination / ENCRYPTED_NAME
            with z.open(info) as src, path.open("xb") as out:
                shutil.copyfileobj(src, out, length=1024 * 1024)
            return path
    except (OSError, zipfile.BadZipFile, EOFError) as exc:
        raise DeliveryError("Downloaded Actions ZIP cannot be read safely") from exc


def save_verified_to_downloads(downloads: Path, filename: str, blob: bytes) -> Path:
    if not downloads.is_dir():
        raise DeliveryError("Samsung Downloads unavailable; run termux-setup-storage first")
    if not (filename.startswith("flipper-z-f7-update-") and filename.endswith(".tgz") and
            "/" not in filename and "\\" not in filename):
        raise DeliveryError("Invalid native F7 updater filename")
    target = downloads / filename
    if target.is_symlink():
        raise DeliveryError("Refusing a symlink target")
    if target.exists():
        if target.is_file() and file_digest(target) == sha256(blob):
            print("Verified .tgz already in Android Downloads; existing identical file preserved.")
            return target
        raise DeliveryError("An older/different firmware file with this name exists in Downloads; not overwritten")
    # Create exclusively. A racing pre-existing file is NEVER deleted.
    created = False
    try:
        with target.open("xb") as stream:
            created = True
            stream.write(blob)
        if file_digest(target) != sha256(blob):
            raise DeliveryError("Copied firmware checksum failed")
    except BaseException:
        if created:
            target.unlink(missing_ok=True)
        raise
    return target


def execute(downloads: Path, selected: Path, *, visible: bool) -> Path:
    if not selected.is_file() or selected.is_symlink():
        raise DeliveryError("Input file unavailable or symlinked")
    # Keep decrypted candidate off shared Android Downloads; delete at finish.
    with tempfile.TemporaryDirectory(prefix="flipper-audited-f7-") as temp:
        stage = Path(temp)
        if selected.name == ENCRYPTED_NAME:
            print("Using owner-extracted .enc file; outer GitHub ZIP digest cannot be rechecked.")
            encrypted = selected
        elif selected.name == ARTIFACT_STEM + ".zip":
            print("Checking exact GitHub Actions artifact ZIP SHA-256...")
            encrypted = extract_encrypted_from_outer_zip(selected, stage)
            print("GitHub artifact ZIP digest: VERIFIED")
        else:
            raise DeliveryError(
                f"Wrong file: {selected.name}. Choose {ARTIFACT_STEM}.zip "
                f"or the inner {ENCRYPTED_NAME}, not the combined ESP32 ZIP.")
        decrypted = stage / "firmware-delivery.tar.gz"
        print("Decrypting locally and validating native Flipper Zero F7 updater contents...")
        filename, native, source = decrypt_and_verify_artifact(
            encrypted, decrypted, visible=visible)
        if source != SOURCE_REVISION:
            raise DeliveryError(
                f"Wrong firmware source {source}; expected {SOURCE_REVISION}. "
                "An older release can have an equally valid native F7 updater.")
        target = save_verified_to_downloads(downloads, filename, native)
        print("SOURCE REVISION: VERIFIED", source)
        print("F7 UPDATER SHA256:", sha256(native))
        print("FIRMWARE FILE:", filename)
        print("SIZE:", len(native), "bytes")
        print("ANDROID MY FILES: Internal storage > Download")
        print("EXACT PATH:", target)
        print("SUCCESS: native Flipper Zero F7 .tgz extracted and independently checked.")
        print("NO FLASH occurred. Back up current working firmware and use a wired "
              "qFlipper path for the next controlled hardware test.")
        return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        help="Exact path to GitHub Actions ZIP or its inner .tar.gz.enc")
    parser.add_argument("--hide-passphrase", action="store_true",
                        help="Use hidden prompt instead of project's requested visible paste input")
    args = parser.parse_args()
    print("AUDITED F7 only / source", SOURCE_REVISION)
    print("Pinned successful GitHub Actions run", RUN_ID, "/ artifact", ARTIFACT_ID)
    print("No Flipper, Wi-Fi or ESP32 connection is needed for extraction.")
    try:
        downloads = Path.home() / "storage" / "downloads"
        if not downloads.is_dir():
            raise DeliveryError("Android Downloads permission missing; run termux-setup-storage")
        selected = identify_input(args.input, downloads)
        print("INPUT:", selected)
        if not args.hide_passphrase:
            print("SECURITY: Your pasted passphrase will be visible on the phone screen. "
                  "Do not capture or share it.")
        execute(downloads, selected, visible=not args.hide_passphrase)
        return 0
    except (DeliveryError, OSError, ValueError) as exc:
        print("STOP: No firmware was flashed. " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
