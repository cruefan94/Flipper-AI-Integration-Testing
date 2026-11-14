#!/usr/bin/env python3
"""Download, decrypt, and verify a native Flipper AI Momentum .tgz ON DEVICE.

Only for an interactive trusted Termux session. Does not flash firmware, request
untrusted execution approval, read secret environment variables, or publish keys.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

REPOSITORY = "cruefan94/Flipper-AI-Integration-Testing"
WORKFLOW_NAME = "Private Momentum AI compile on public runner"
ARTIFACT_NAME = "encrypted-flipper-ai-mobile-native-tgz-UNTESTED"
ENCRYPTED_NAME = "flipper-ai-native-tgz-delivery.tar.gz.enc"
FORMAT = "flipper-ai-native-tgz-delivery-v1"
MAX_CONTENT = 100 * 1024 * 1024
MAX_FILES = 512
REQUIRED = {"update.fuf", "updater.bin", "firmware.dfu"}
NAME_RE = re.compile(r"flipper-z-f7-update-[A-Za-z0-9._-]+\.tgz\Z")


class DeliveryError(Exception):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(command: list[str], *, interactive: bool = False) -> str:
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=not interactive,
            text=True,
            timeout=300 if interactive else 90,
        )
    except FileNotFoundError as exc:
        raise DeliveryError(f"Required program unavailable: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        # Do not print command arguments or secrets.
        error = (exc.stderr or "").strip() if not interactive else ""
        raise DeliveryError(f"{command[0]} failed ({exc.returncode}): {error[:400]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise DeliveryError(f"{command[0]} timed out") from exc
    return completed.stdout if not interactive else ""


def github(path: str) -> dict:
    if not path.startswith("repos/") or ".." in path or " " in path:
        raise DeliveryError("Unsafe GitHub API path")
    try:
        result = json.loads(run(["gh", "api", path]))
        if not isinstance(result, dict):
            raise DeliveryError("Unexpected GitHub response")
        return result
    except ValueError as exc:
        raise DeliveryError("Invalid response from GitHub") from exc


def find_successful_run(requested: int | None = None) -> tuple[int, int]:
    if requested is None:
        data = github(f"repos/{REPOSITORY}/actions/runs?per_page=50")
        eligible = [
            v for v in data.get("workflow_runs", [])
            if v.get("name") == WORKFLOW_NAME
            and v.get("head_branch") == "main"
            and v.get("status") == "completed"
            and v.get("conclusion") == "success"
        ]
        if not eligible:
            raise DeliveryError("No completed successful main-branch firmware build found")
        eligible.sort(key=lambda v: (v.get("created_at", ""), v.get("id", 0)), reverse=True)
        selected = eligible[0]
    else:
        if requested < 1:
            raise DeliveryError("Invalid Actions run ID")
        selected = github(f"repos/{REPOSITORY}/actions/runs/{requested}")
        if (selected.get("name") != WORKFLOW_NAME
                or selected.get("head_branch") != "main"
                or selected.get("status") != "completed"
                or selected.get("conclusion") != "success"):
            raise DeliveryError("Selected run is not a successful main-branch AI firmware build")
    run_id = int(selected["id"])
    data = github(f"repos/{REPOSITORY}/actions/runs/{run_id}/artifacts?per_page=100")
    eligible_artifacts = [
        a for a in data.get("artifacts", [])
        if a.get("name") == ARTIFACT_NAME and not a.get("expired")
    ]
    if len(eligible_artifacts) != 1:
        raise DeliveryError("No unique non-expired encrypted native firmware artifact")
    return run_id, int(eligible_artifacts[0]["id"])


def tar_members(archive: tarfile.TarFile, *, max_files: int = MAX_FILES):
    members = archive.getmembers()
    if not members or len(members) > max_files:
        raise DeliveryError("Unexpected archive entry count")
    names = set()
    for member in members:
        raw = member.name
        path = PurePosixPath(raw)
        if (not raw or raw.startswith("/") or "\\" in raw
                or any(part in ("..", ".") for part in raw.split("/"))
                or str(path) != raw.rstrip("/")):
            raise DeliveryError("Unsafe path inside archive")
        if not (member.isfile() or member.isdir()):
            raise DeliveryError("Archive contains a link or unsupported special file")
        if raw in names:
            raise DeliveryError("Duplicate file in archive")
        if member.size < 0 or member.size > MAX_CONTENT:
            raise DeliveryError("Archive member exceeds safe size limit")
        names.add(raw)
    return members


def read_member(archive: tarfile.TarFile, member: tarfile.TarInfo) -> bytes:
    if not member.isfile() or member.size > MAX_CONTENT:
        raise DeliveryError("Invalid archive member")
    stream = archive.extractfile(member)
    if stream is None:
        raise DeliveryError("Unreadable archive member")
    value = stream.read(MAX_CONTENT + 1)
    if len(value) != member.size:
        raise DeliveryError("Archive member size mismatch")
    return value


def validate_native(tgz_data: bytes, manifest: dict) -> None:
    if len(tgz_data) > MAX_CONTENT:
        raise DeliveryError("Native firmware too large")
    name = manifest.get("updater")
    if not isinstance(name, str) or not re.fullmatch(r"f7-update-[A-Za-z0-9._-]+", name):
        raise DeliveryError("Invalid Flipper Zero F7 updater directory")
    records = manifest.get("files")
    if not isinstance(records, dict) or not REQUIRED.issubset(records):
        raise DeliveryError("Native updater required files missing")
    visited: set[str] = set()
    try:
        with tarfile.open(fileobj=io.BytesIO(tgz_data), mode="r:gz") as native:
            for member in tar_members(native):
                path = PurePosixPath(member.name)
                if path.parts[0] != name:
                    raise DeliveryError("Firmware updater directory mismatch")
                if member.isdir():
                    continue
                if len(path.parts) != 2 or path.parts[1] not in records:
                    raise DeliveryError("Unexpected firmware archive member")
                relative = path.parts[1]
                if relative in visited:
                    raise DeliveryError("Duplicate firmware archive member")
                raw = read_member(native, member)
                info = records[relative]
                if (not isinstance(info, dict) or len(raw) != info.get("size")
                        or sha256(raw) != info.get("sha256")):
                    raise DeliveryError(f"Native firmware manifest mismatch: {relative}")
                if relative == "update.fuf":
                    desc = raw.decode("utf-8", errors="replace")
                    if (not any(s.strip() == "Target: 7" for s in desc.splitlines())
                            or not any(s.strip() == "Loader: updater.bin" for s in desc.splitlines())
                            or not any(s.strip() == "Firmware: firmware.dfu" for s in desc.splitlines())
                            or "Flipper firmware upgrade configuration" not in desc):
                        raise DeliveryError("Native firmware manifest target/loader mismatch")
                visited.add(relative)
    except (OSError, tarfile.TarError, EOFError) as exc:
        raise DeliveryError("Native firmware archive is unreadable") from exc
    if visited != set(records):
        raise DeliveryError("Native firmware file inventory does not match manifest")


def verify_delivery(path: Path) -> tuple[str, bytes, str]:
    if not path.is_file() or path.stat().st_size > MAX_CONTENT:
        raise DeliveryError("Invalid decrypted delivery archive")
    try:
        with tarfile.open(path, mode="r:gz") as archive:
            members = tar_members(archive, max_files=4)
            if not all(x.isfile() for x in members):
                raise DeliveryError("Delivery archive contains unexpected directories")
            mapping = {m.name: m for m in members}
            if "SHA256-manifest.json" not in mapping or "READ_ME_FIRST.txt" not in mapping:
                raise DeliveryError("Delivery manifest or warning notice missing")
            manifest = json.loads(read_member(archive, mapping["SHA256-manifest.json"]))
            if (manifest.get("format") != FORMAT
                    or manifest.get("target") != "Flipper Zero F7"):
                raise DeliveryError("Unsupported delivery format or hardware target")
            record = manifest.get("native_tgz")
            if not isinstance(record, dict):
                raise DeliveryError("Native firmware record missing")
            filename = record.get("name")
            if not isinstance(filename, str) or not NAME_RE.fullmatch(filename):
                raise DeliveryError("Invalid native firmware filename")
            if set(mapping) != {filename, "SHA256-manifest.json", "READ_ME_FIRST.txt"}:
                raise DeliveryError("Delivery contains unexpected files")
            native = read_member(archive, mapping[filename])
            if len(native) != record.get("size") or sha256(native) != record.get("sha256"):
                raise DeliveryError("Native firmware checksum mismatch")
            validate_native(native, manifest)
            return filename, native, str(manifest.get("source_revision", "unknown"))
    except (OSError, tarfile.TarError, EOFError, ValueError, TypeError, KeyError) as exc:
        raise DeliveryError(f"Could not verify firmware delivery: {exc}") from exc


def save_candidate(destination: Path, filename: str, data: bytes) -> Path:
    if not NAME_RE.fullmatch(filename):
        raise DeliveryError("Unsafe output filename")
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    target = destination / filename
    if target.exists():
        if target.is_file() and sha256(target.read_bytes()) == sha256(data):
            return target
        target = destination / (filename[:-4] + "-" + sha256(data)[:12] + ".tgz")
    with target.open("xb") as stream:
        os.chmod(target, 0o600)
        stream.write(data)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", type=int, help="Verified successful main-branch run; default newest")
    parser.add_argument("--share-downloads", action="store_true",
                        help="Copy verified .tgz into Android Downloads (requires Termux storage permission)")
    args = parser.parse_args()
    print("Experimental AI Momentum F7 firmware. NOT hardware tested. No flashing will be performed.")
    print("Download requires authenticated GitHub CLI. Decryption happens only on this phone.")
    try:
        shutil.which("openssl") or (_ for _ in ()).throw(
            DeliveryError("OpenSSL is missing. Install the Termux openssl package."))
        run_id, artifact_id = find_successful_run(args.run_id)
        print(f"Selected successful build {run_id}, encrypted artifact {artifact_id}.")
        work = Path.home() / "flipper-ai-workspace" / "firmware-updates"
        work.mkdir(mode=0o700, parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="staging-", dir=work) as staged:
            temp = Path(staged)
            run(["gh", "run", "download", str(run_id), "--repo", REPOSITORY,
                 "--name", ARTIFACT_NAME, "--dir", str(temp)])
            encrypted = temp / ENCRYPTED_NAME
            if not encrypted.is_file() or encrypted.stat().st_size > MAX_CONTENT:
                raise DeliveryError("Encrypted artifact missing or unexpectedly large")
            decrypted = temp / "verified-delivery.tar.gz"
            print("OpenSSL will prompt for your existing private artifact passphrase.")
            print("Never paste the passphrase into GitHub, the Termux issue bridge, or chat.")
            run(["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-iter", "250000",
                 "-salt", "-in", str(encrypted), "-out", str(decrypted)], interactive=True)
            filename, firmware, source = verify_delivery(decrypted)
            saved = save_candidate(work, filename, firmware)
            print(f"Validated source {source}; firmware SHA256 {sha256(firmware)}.")
            print(f"Verified native F7 firmware file: {saved}")
            if args.share_downloads:
                downloads = Path.home() / "storage" / "downloads"
                if not downloads.is_dir():
                    raise DeliveryError("Downloads access not granted. Run termux-setup-storage locally.")
                shared = save_candidate(downloads / "FlipperAI_Firmware", filename, firmware)
                print(f"Copied verified firmware to Android Downloads: {shared}")
        print("Candidate extracted and verified. Flipper firmware was NOT flashed.")
        print("Confirm backup/qFlipper recovery before attempting a physical device update.")
        return 0
    except DeliveryError as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
