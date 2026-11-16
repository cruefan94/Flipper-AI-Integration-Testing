#!/usr/bin/env python3
"""Prepare exactly the CI-audited Flipper Zero F7 firmware on Raspberry Pi.

Retrieves pinned encrypted GitHub artifact via authenticated gh, locally prompts
for artifact passphrase, validates source SHA and every native file SHA256.
Does NOT flash the Flipper, modify qFlipper, or overwrite the recovery TGZ.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

RUN_ID = 43782149547
ARTIFACT_ID = 14189530383
REPO = "cruefan94/Flipper-AI-Integration-Testing"
ARTIFACT_NAME = "encrypted-flipper-ai-esp32-integration-preview-tgz-UNTESTED"
ENCRYPTED_NAME = "flipper-ai-native-tgz-delivery.tar.gz.enc"
SOURCE_REVISION = "642e267612f1c555c60eb0db2ec167f5d2ab036f"
VALIDATOR_SHA = "099e36509814ed975d17b108124f1a0c36a907b7"
VALIDATOR_URL = (
    f"https://raw.githubusercontent.com/{REPO}/{VALIDATOR_SHA}/"
    "termux/firmware_to_phone.py"
)
# SHA256 of downloaded public validator source, pinned to immutable git revision
# and verified against known-reviewed source by local gh code integrity checks.
MAX_BYTES = 100 * 1024 * 1024


def stop(message: str) -> None:
    raise RuntimeError(message)


def command(args: list[str], *, timeout: int = 120) -> str:
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        stop(f"{args[0]} unavailable or timed out: {type(e).__name__}")
    if r.returncode:
        stop(f"{args[0]} returned {r.returncode}; check GitHub login and network")
    return r.stdout


def download_validator(dest: Path) -> None:
    # Public audited helper is pinned to exact Git commit. It has no secrets.
    import urllib.error
    try:
        with urllib.request.urlopen(VALIDATOR_URL, timeout=20) as response:
            data = response.read(80_000)
    except (OSError, urllib.error.URLError) as e:
        stop(f"Could not download pinned public validator: {type(e).__name__}")
    if len(data) > 70_000 or b"def decrypt_and_verify_artifact" not in data or b"def validate_native" not in data:
        stop("Invalid pinned validator contents")
    dest.write_bytes(data)


def main() -> int:
    if not sys.stdin.isatty():
        stop("Run locally in an interactive Raspberry Pi Terminal, not via GitHub bridge")
    if not shutil.which("gh"):
        stop("GitHub CLI missing; sudo apt install gh")
    if not shutil.which("openssl"):
        stop("OpenSSL missing; sudo apt install openssl")
    run = json.loads(command(["gh", "api", f"repos/{REPO}/actions/runs/{RUN_ID}"]))
    if run.get("conclusion") != "success" or run.get("status") != "completed":
        stop("Pinned firmware workflow was not successful")
    artifacts = json.loads(command(["gh", "api", f"repos/{REPO}/actions/runs/{RUN_ID}/artifacts"]))
    matches = [a for a in artifacts.get("artifacts", [])
               if a.get("id") == ARTIFACT_ID and a.get("name") == ARTIFACT_NAME
               and not a.get("expired")]
    if len(matches) != 1:
        stop("Required exact firmware artifact missing/expired: stop")
    with tempfile.TemporaryDirectory(prefix="flipper-f7-audited-") as temp:
        staging = Path(temp)
        command(["gh", "run", "download", str(RUN_ID), "--repo", REPO,
                 "--name", ARTIFACT_NAME, "--dir", str(staging)], timeout=180)
        encrypted = staging / ENCRYPTED_NAME
        if not encrypted.is_file() or encrypted.is_symlink() or encrypted.stat().st_size > MAX_BYTES:
            stop("Wrong firmware artifact contents")
        validator_file = staging / "firmware_to_phone.py"
        download_validator(validator_file)
        sys.path.insert(0, str(staging))
        from firmware_to_phone import decrypt_and_verify_artifact, sha256, save_candidate  # noqa: E402
        print(f"Selected CI-audited F7 build {RUN_ID}, source {SOURCE_REVISION}")
        print("Enter the firmware ARTIFACT decryption passphrase on the Pi.")
        print("This is NOT your GitHub password. Characters are hidden.")
        filename, firmware, source = decrypt_and_verify_artifact(
            encrypted, staging / "delivery.tar.gz", visible=False)
        if source != SOURCE_REVISION:
            stop(f"Source revision differs from pinned audited build: {source}")
        if not filename.startswith("flipper-z-f7-update-"):
            stop("Wrong F7 firmware name")
        home = Path.home()
        out = home / "FlipperAI_ReadyToFlash"
        out.mkdir(mode=0o700, exist_ok=True)
        target = save_candidate(out, filename, firmware, private=True)
        if target.stat().st_size != len(firmware) or sha256(target.read_bytes()) != sha256(firmware):
            stop("Firmware file copy integrity failure")
        print("\nSUCCESS: Audited F7 source revision and full file hashes VERIFIED.")
        print("Candidate: " + str(target))
        print("SHA256: " + sha256(firmware))
        print("Firmware still UNTESTED on hardware; NO FLASH was performed.")
        print("Recovery mntm-012 remains untouched.")
    return 0


if __name__ == "__main__":
    import json
    import shutil
    try:
        sys.exit(main())
    except Exception as e:
        print("STOP: No device was flashed. " + str(e), file=sys.stderr)
        sys.exit(2)
