#!/usr/bin/env python3
"""Validate the native F7 Momentum .tgz and wrap it for encrypted, private delivery.

The public CI runner must never upload unencrypted private firmware or model keys.
This tool only packages files built by the pinned upstream Momentum build system.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

MAX_TGZ_BYTES = 128 * 1024 * 1024
MAX_MEMBERS = 512
REQUIRED_FILES = {"update.fuf", "firmware.dfu", "updater.bin"}
MANIFEST = "SHA256-manifest.json"
NOTICE = "READ_ME_FIRST.txt"
FORMAT = "flipper-ai-native-tgz-delivery-v1"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_members(archive: tarfile.TarFile):
    members = archive.getmembers()
    if not members or len(members) > MAX_MEMBERS:
        raise ValueError("Missing or excessive archive entries")
    seen = set()
    for member in members:
        name = member.name
        path = PurePosixPath(name)
        if (not name or name.startswith("/") or "\\" in name
                or ".." in path.parts or "." in path.parts):
            raise ValueError(f"Unsafe archive path: {name!r}")
        if not (member.isfile() or member.isdir()):
            raise ValueError("Archive links and special files are forbidden")
        if name in seen:
            raise ValueError("Duplicate archive member")
        seen.add(name)
    return members


def verify_native_tgz(blob: bytes, updater_name: str, file_records: dict):
    if not (blob and len(blob) <= MAX_TGZ_BYTES):
        raise ValueError("Invalid updater .tgz size")
    if not updater_name.startswith("f7-update-") or "/" in updater_name:
        raise ValueError("Expected one Flipper Zero F7 updater folder")
    if not REQUIRED_FILES.issubset(file_records):
        raise ValueError("Updater is missing required Flipper firmware files")
    seen = set()
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
        for member in checked_members(archive):
            path = PurePosixPath(member.name)
            if path.parts[0] != updater_name:
                raise ValueError("Native .tgz has an unexpected top-level path")
            if member.isdir():
                continue
            if len(path.parts) != 2:
                raise ValueError("Unexpected nested updater file")
            relative = path.parts[1]
            if relative not in file_records or relative in seen:
                raise ValueError("Native .tgz file inventory mismatch")
            entry = archive.extractfile(member)
            if entry is None:
                raise ValueError("Cannot read native updater member")
            data = entry.read()
            record = file_records[relative]
            if len(data) != record["size"] or digest(data) != record["sha256"]:
                raise ValueError(f"Native updater hash mismatch: {relative}")
            seen.add(relative)
    if seen != set(file_records):
        raise ValueError("Native updater missing one or more manifest files")


def build_package(dist: Path, output: Path, source: str, momentum: str) -> Path:
    if not dist.is_dir():
        raise ValueError("Momentum dist/f7-C folder not found")
    folders = sorted(p for p in dist.glob("f7-update-*") if p.is_dir())
    native = sorted(p for p in dist.glob("flipper-z-f7-update-*.tgz") if p.is_file())
    if len(folders) != 1 or len(native) != 1:
        raise ValueError("Expected exactly one F7 updater directory and native .tgz")
    folder, updater_tgz = folders[0], native[0]
    file_records = {}
    for path in sorted(folder.rglob("*")):
        if path.is_symlink() or (not path.is_file() and not path.is_dir()):
            raise ValueError("Updater contains an unsafe filesystem entry")
        if path.is_dir():
            continue
        relative = path.relative_to(folder).as_posix()
        if "/" in relative or relative in file_records:
            raise ValueError("Unexpected updater folder hierarchy")
        data = path.read_bytes()
        if not data:
            raise ValueError(f"Empty updater file: {relative}")
        file_records[relative] = {"size": len(data), "sha256": digest(data)}
    if not REQUIRED_FILES.issubset(file_records):
        raise ValueError("Missing firmware.dfu, updater.bin, or update.fuf")
    fuf = (folder / "update.fuf").read_text(encoding="utf-8", errors="replace")
    if ("Flipper firmware upgrade configuration" not in fuf
            or not any(line.strip() == "Target: 7" for line in fuf.splitlines())
            or not any(line.strip() == "Loader: updater.bin" for line in fuf.splitlines())):
        raise ValueError("Flipper update manifest has the wrong format/target/loader")
    blob = updater_tgz.read_bytes()
    verify_native_tgz(blob, folder.name, file_records)
    output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "format": FORMAT,
        "target": "Flipper Zero F7",
        "source_revision": source,
        "momentum_revision": momentum,
        "updater": folder.name,
        "native_tgz": {"name": updater_tgz.name, "size": len(blob), "sha256": digest(blob)},
        "files": file_records,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    notice = (
        "PRIVATE EXPERIMENTAL CUSTOM MOMENTUM + FLIPPER AI FIRMWARE\n"
        "COMPILED AND PACKAGED; NOT TESTED ON FLIPPER ZERO HARDWARE.\n"
        "After decryption, ONLY the included flipper-z-f7-update-*.tgz is a native\n"
        "Flipper update package. Do not flash the outer ZIP, encrypted archive,\n"
        "or delivery .tar.gz. Confirm SD backup and qFlipper recovery first.\n"
        "Keep this private and verify the SHA256-manifest.json before use.\n"
    ).encode()
    delivery = output / "flipper-ai-native-tgz-delivery.tar.gz"
    with tarfile.open(delivery, mode="w:gz") as archive:
        for name, data in (
            (updater_tgz.name, blob),
            (MANIFEST, manifest_bytes),
            (NOTICE, notice),
        ):
            member = tarfile.TarInfo(name)
            member.mode = 0o600
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
    verify_package(delivery)
    return delivery


def verify_package(delivery: Path) -> str:
    with tarfile.open(delivery, mode="r:gz") as archive:
        members = checked_members(archive)
        if not all(m.isfile() for m in members):
            raise ValueError("Delivery must contain only three ordinary files")
        by_name = {member.name: member for member in members}
        if MANIFEST not in by_name or NOTICE not in by_name or len(by_name) != 3:
            raise ValueError("Delivery inventory is invalid")
        stream = archive.extractfile(MANIFEST)
        if stream is None:
            raise ValueError("Missing delivery manifest")
        manifest = json.load(stream)
        if manifest.get("format") != FORMAT or manifest.get("target") != "Flipper Zero F7":
            raise ValueError("Unsupported delivery format/target")
        record = manifest["native_tgz"]
        name = record["name"]
        if not name.startswith("flipper-z-f7-update-") or not name.endswith(".tgz"):
            raise ValueError("Not a native Flipper F7 updater filename")
        if set(by_name) != {MANIFEST, NOTICE, name}:
            raise ValueError("Unexpected files in delivery")
        stream = archive.extractfile(name)
        if stream is None:
            raise ValueError("Missing native updater")
        blob = stream.read(MAX_TGZ_BYTES + 1)
        if len(blob) != record["size"] or digest(blob) != record["sha256"]:
            raise ValueError("Delivery .tgz hash/size mismatch")
        verify_native_tgz(blob, manifest["updater"], manifest["files"])
        return name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    pack = subs.add_parser("pack")
    pack.add_argument("--dist", type=Path, required=True)
    pack.add_argument("--out", type=Path, required=True)
    pack.add_argument("--source-revision", required=True)
    pack.add_argument("--momentum-revision", required=True)
    check = subs.add_parser("verify")
    check.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "pack":
        archive = build_package(args.dist, args.out, args.source_revision, args.momentum_revision)
        print(f"Native F7 .tgz verified, ready for passphrase-encrypted delivery: {archive}")
    else:
        print(f"Verified native F7 updater package: {verify_package(args.archive)}")


if __name__ == "__main__":
    main()
