#!/usr/bin/env python3
"""Flipper AI Raspberry Pi 4B companion: local AI + private, read-only GitHub bridge.

No remote shell, no automatic flashing, no privileged operations, no public server.
Install on the Pi (not the phone); private GitHub Issues connect it to this project.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import time

QUEUE = "cruefan94/Flipper-AI-Momentum-"
AUTHOR = "cruefan94"
DEVICE = "raspberrypi4b"
PREFIX = "[Pi] "
STATE = Path.home() / ".local" / "state" / "flipper-ai-pi-bridge"
REPOS = {
    "momentum": "cruefan94/Flipper-AI-Momentum-",
    "android": "cruefan94/Flipper-AI-Android-Satellite",
    "testing": "cruefan94/Flipper-AI-Integration-Testing",
}
OPS = {"diagnostics", "usb_status", "firmware_inventory",
       "workflow_runs", "qflipper_status", "launch_qflipper"}
MAX_TGZ = 128 * 1024 * 1024
MAX_EXPANDED = 256 * 1024 * 1024
MAX_MEMBERS = 512


class BridgeError(Exception):
    pass


def redact(value: object) -> str:
    text = str(value)
    patterns = (
        r"(?i)(?:github_pat_|gh[pousr]_)[A-Za-z0-9_]{12,}",
        r"(?i)(?:sk-|sk-proj-)[A-Za-z0-9_-]{12,}",
        r"(?i)(?:bearer\s+)[A-Za-z0-9._~-]{12,}",
        r"(?i)((?:OPENAI_API_KEY|GH_TOKEN|GITHUB_TOKEN|DEVICE_TOKEN)\s*[=:]\s*)\S+",
    )
    for pattern in patterns:
        text = re.sub(pattern, "[REDACTED]", text)
    return text[:5500]


def capture(argv: list[str], *, seconds: int = 7) -> tuple[int, str]:
    try:
        done = subprocess.run(argv, capture_output=True, text=True, timeout=seconds)
        return done.returncode, redact((done.stdout or "") + (done.stderr or ""))
    except (OSError, subprocess.TimeoutExpired):
        return 1, "Not installed, unavailable or timed out"


def gh(method: str, path: str, payload: dict | None = None) -> object:
    if method not in ("GET", "POST", "PATCH"):
        raise BridgeError("Invalid GitHub method")
    if not path.startswith("repos/") or ".." in path or any(c in path for c in " \n\r\\"):
        raise BridgeError("Invalid GitHub API path")
    args = ["gh", "api", "--method", method, path]
    if payload is not None:
        args.extend(["--input", "-"])
    try:
        done = subprocess.run(
            args, input=json.dumps(payload) if payload is not None else None,
            capture_output=True, text=True, timeout=25)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BridgeError("GitHub CLI is unavailable or timed out") from exc
    if done.returncode:
        raise BridgeError("GitHub API unavailable; check 'gh auth status' on the Pi")
    try:
        return json.loads(done.stdout) if done.stdout.strip() else {}
    except ValueError as exc:
        raise BridgeError("GitHub returned invalid JSON") from exc


def qflipper_executable() -> str | None:
    for name in ("qFlipper", "qflipper"):
        found = shutil.which(name)
        if found:
            return found
    for location in (Path.home() / "Applications" / "qFlipper.AppImage",
                     Path.home() / "Applications" / "qflipper.AppImage"):
        if location.is_file() and os.access(location, os.X_OK) and not location.is_symlink():
            return str(location)
    return None


def usb_status() -> dict:
    # Avoid serial numbers and hardware identifiers in remote GitHub reports.
    return {
        "ttyACM": [p.name for p in sorted(Path("/dev").glob("ttyACM*")) if not p.is_symlink()][:8],
        "ttyUSB": [p.name for p in sorted(Path("/dev").glob("ttyUSB*")) if not p.is_symlink()][:8],
        "usb_serial_by_id_count": len(list(Path("/dev/serial/by-id").glob("*"))) if
            Path("/dev/serial/by-id").is_dir() else 0,
        "qflipper_executable_found": qflipper_executable() is not None,
        "note": "A USB serial device is not proof of a connected Flipper. Check qFlipper's device display.",
    }


def diagnostics() -> dict:
    bluetooth = capture(["bluetoothctl", "show"])
    adapter_power = "unknown"
    if bluetooth[0] == 0:
        for line in bluetooth[1].splitlines():
            if line.strip().startswith("Powered:"):
                adapter_power = line.split(":", 1)[1].strip().lower()
    return {
        "device": DEVICE,
        "system": platform.system(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "bluetooth_adapter_powered": adapter_power,
        "github_cli_present": shutil.which("gh") is not None,
        "qflipper_present": qflipper_executable() is not None,
        "usb": usb_status(),
        "transport": "Private GitHub issue queue; Pi must have internet (Wi-Fi or tethering)",
        "automatic_flashing": False,
    }


def check_native_f7(file: Path) -> dict:
    if not file.is_file() or file.is_symlink() or file.stat().st_size > MAX_TGZ:
        raise BridgeError("Not a regular F7 updater or archive too large")
    h = hashlib.sha256()
    with file.open("rb") as fp:
        for block in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(block)
    try:
        with tarfile.open(file, "r:gz") as archive:
            members = archive.getmembers()
            if not 3 <= len(members) <= MAX_MEMBERS:
                raise BridgeError("Invalid archive inventory size")
            seen = set()
            updater_name = None
            found = {}
            expanded = 0
            for member in members:
                path = PurePosixPath(member.name)
                if (member.name.startswith("/") or "\\" in member.name or
                        ".." in path.parts or "." in path.parts or
                        not (member.isfile() or member.isdir()) or
                        member.name in seen):
                    raise BridgeError("Unsafe member in updater")
                seen.add(member.name)
                if not path.parts or not path.parts[0].startswith("f7-update-") or len(path.parts) > 2:
                    raise BridgeError("Unexpected native updater folder")
                if updater_name is None:
                    updater_name = path.parts[0]
                elif path.parts[0] != updater_name:
                    raise BridgeError("Multiple updater directories")
                if member.isfile():
                    if len(path.parts) != 2:
                        raise BridgeError("Unexpected updater file")
                    expanded += member.size
                    if expanded > MAX_EXPANDED or member.size > MAX_TGZ:
                        raise BridgeError("Unpacked F7 contents exceed limit")
                    if path.parts[1] in ("update.fuf", "firmware.dfu", "updater.bin"):
                        if path.parts[1] in found:
                            raise BridgeError("Duplicate required firmware file")
                        if path.parts[1] == "update.fuf":
                            data = archive.extractfile(member)
                            if data is None:
                                raise BridgeError("Unreadable update.fuf")
                            found["update.fuf"] = data.read(8192).decode("utf-8", "replace")
                        else:
                            found[path.parts[1]] = member.size > 0
            if not {"update.fuf", "firmware.dfu", "updater.bin"}.issubset(found):
                raise BridgeError("Native F7 update missing required files")
            fuf = found["update.fuf"].splitlines()
            if not (any(x.strip() == "Target: 7" for x in fuf) and
                    any(x.strip() == "Loader: updater.bin" for x in fuf) and
                    any(x.strip() == "Firmware: firmware.dfu" for x in fuf) and
                    found["firmware.dfu"] and found["updater.bin"]):
                raise BridgeError("Wrong firmware hardware target or updater contents")
    except (tarfile.TarError, EOFError, OSError) as exc:
        raise BridgeError("Invalid native TGZ archive") from exc
    return {
        "name": file.name,
        "size": file.stat().st_size,
        "sha256": h.hexdigest(),
        "f7_native_structure": "validated",
        "firmware_source_revision": "not independently authenticated from native TGZ alone",
        "hardware_tested": False,
    }


def firmware_inventory() -> dict:
    folders = [
        Path.home() / "Downloads",
        Path.home() / "downloads",
        Path.home() / "flipper-ai-verified-5501cb9",
        Path.home() / "flipper-ai-workspace" / "firmware-updates",
    ]
    files = {}
    for directory in folders:
        if not directory.is_dir() or directory.is_symlink():
            continue
        for file in sorted(directory.glob("flipper-z-f7-update-*.tgz")):
            if file.is_symlink() or not file.is_file():
                continue
            if file.name not in files and len(files) < 12:
                try:
                    files[file.name] = check_native_f7(file)
                except BridgeError as exc:
                    files[file.name] = {"name": file.name, "validation": redact(exc)}
    return {"count": len(files), "candidates": list(files.values()),
            "note": "No device writes; archive shape alone cannot prove release authenticity"}


def qflipper_status() -> dict:
    exe = qflipper_executable()
    # Process matches are informational only; never print process args.
    code, result = capture(["pgrep", "-f", r"[/]qFlipper|[/]qflipper"], seconds=3)
    return {"installed": bool(exe), "running": code == 0 and bool(result.strip()),
            "can_launch_with_local_approval": bool(exe),
            "flashing_started": False}


def workflow_runs(alias: str) -> dict:
    if alias not in REPOS:
        raise BridgeError("Unknown repository alias")
    items = gh("GET", f"repos/{REPOS[alias]}/actions/runs?per_page=4")
    if not isinstance(items, dict):
        raise BridgeError("Unexpected GitHub workflow response")
    return {"repository": alias, "runs": [
        {"id": x.get("id"), "name": x.get("name"),
         "status": x.get("status"), "conclusion": x.get("conclusion")}
        for x in items.get("workflow_runs", [])[:4] if isinstance(x, dict)]}


def execute(operation: str, args: dict) -> dict:
    if operation == "diagnostics":
        return diagnostics()
    if operation == "usb_status":
        return usb_status()
    if operation == "firmware_inventory":
        return firmware_inventory()
    if operation == "workflow_runs":
        return workflow_runs(args.get("repo", "testing"))
    if operation == "qflipper_status":
        return qflipper_status()
    raise BridgeError("Unrecognized or approval-required operation")


def parse_issue(issue: dict) -> dict | None:
    if (not isinstance(issue, dict) or issue.get("pull_request") or
            issue.get("state", "open") != "open" or
            not str(issue.get("title", "")).startswith(PREFIX) or
            str(issue.get("user", {}).get("login", "")).lower() != AUTHOR):
        return None
    try:
        body = json.loads(issue.get("body") or "")
    except (TypeError, ValueError):
        return None
    if (not isinstance(body, dict) or body.get("schema") != 1 or
            body.get("device") != DEVICE or body.get("operation") not in OPS or
            not isinstance(body.get("args"), dict)):
        return None
    if body["operation"] != "workflow_runs" and body["args"]:
        return None
    if body["operation"] == "workflow_runs" and set(body["args"]) - {"repo"}:
        return None
    return body


def state_file(number: int, suffix: str) -> Path:
    return STATE / f"{number}.{suffix}"


def claim(path: Path) -> bool:
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(descriptor)
        return True
    except FileExistsError:
        return False


def atomic_json(path: Path, payload: dict) -> None:
    temp = state_file(os.getpid(), "tmp")
    fd = os.open(temp, os.O_CREAT | os.O_WRONLY | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w") as output:
            json.dump(payload, output)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def report_pending() -> None:
    for file in sorted(STATE.glob("*.result.json")):
        number = int(file.name.split(".", 1)[0])
        if state_file(number, "reported").exists():
            continue
        record = json.loads(file.read_text())
        message = ("Flipper AI Raspberry Pi 4B bridge (read-only; no flashing)\n\n"
                   + "Operation: " + record["operation"] + "\n"
                   + "Result:\n~~~json\n"
                   + redact(json.dumps(record["result"], indent=2)) + "\n~~~")
        try:
            if not state_file(number, "commented").exists():
                gh("POST", f"repos/{QUEUE}/issues/{number}/comments", {"body": message})
                claim(state_file(number, "commented"))
            gh("PATCH", f"repos/{QUEUE}/issues/{number}", {"state": "closed"})
            claim(state_file(number, "reported"))
        except BridgeError:
            # Preserve local result; retry comment/close on next poll.
            pass


def poll_once() -> None:
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(STATE, 0o700)
    report_pending()
    for page in range(1, 4):
        issues = gh("GET", f"repos/{QUEUE}/issues?state=open&per_page=100&page={page}")
        if not isinstance(issues, list):
            raise BridgeError("Unexpected GitHub issue list")
        for issue in issues:
            task = parse_issue(issue)
            if task is None:
                continue
            number = int(issue["number"])
            if not claim(state_file(number, "claimed")):
                continue
            if task["operation"] == "launch_qflipper":
                atomic_json(state_file(number, "pending.json"), task)
                print(f"qFlipper launch #{number} requires LOCAL approval: "
                      f"python3 raspberry_pi/pi_bridge.py approve {number}", flush=True)
                continue
            try:
                outcome = execute(task["operation"], task["args"])
            except Exception as exc:
                outcome = {"error": redact(exc)}
            atomic_json(state_file(number, "result.json"),
                        {"operation": task["operation"], "result": outcome})
            print("Completed read-only Pi request #" + str(number), flush=True)
        if len(issues) < 100:
            break
    report_pending()


def approve(number: int) -> None:
    pending = state_file(number, "pending.json")
    if (not pending.is_file() or state_file(number, "result.json").exists() or
            state_file(number, "launched").exists()):
        raise BridgeError("No new Pi approval request exists for that number")
    task = json.loads(pending.read_text())
    if task["operation"] != "launch_qflipper":
        raise BridgeError("Only launching qFlipper can be approved")
    live = gh("GET", f"repos/{QUEUE}/issues/{number}")
    if not isinstance(live, dict) or parse_issue(live) != task:
        raise BridgeError("Original owner issue closed or modified; refusing")
    print("This starts qFlipper's GUI on the Raspberry Pi. It does NOT flash.")
    if input(f"Type YES on the Pi keyboard to launch qFlipper for issue #{number}: ") != "YES":
        raise BridgeError("Not approved locally")
    exe = qflipper_executable()
    if not exe:
        raise BridgeError("qFlipper executable not found")
    if not claim(state_file(number, "launched")):
        raise BridgeError("Already attempted to launch")
    try:
        subprocess.Popen([exe], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
        result = {"qflipper_launched": True, "firmware_flashing_started": False}
    except OSError as exc:
        result = {"qflipper_launched": False, "error": redact(exc)}
    atomic_json(state_file(number, "result.json"),
                {"operation": "launch_qflipper", "result": result})
    report_pending()


def ask(prompt: str, *, with_diagnostics: bool = False) -> str:
    """Interactive, opt-in ONLINE AI. This API is billed separately from ChatGPT."""
    if not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 2500:
        raise BridgeError("Enter a non-empty question up to 2,500 characters")
    if not os.environ.get("OPENAI_API_KEY"):
        raise BridgeError(
            "Pi AI API is not configured. Use the read-only diagnostics and private "
            "GitHub bridge for free; optional OpenAI API needs a separately billed key.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise BridgeError("Optional API client missing: python3 -m pip install openai") from exc
    model = os.getenv("FLIPPER_PI_OPENAI_MODEL", "gpt-5.5")
    context = ""
    if with_diagnostics:
        # Only the explicit flag authorizes sending limited Pi diagnostics to the API.
        context = "\nUser explicitly supplied this sanitized Pi status:\n" + json.dumps(diagnostics())
    client = OpenAI(timeout=30.0, max_retries=1)
    response = client.responses.create(
        model=model,
        store=False,
        instructions=("You are a Raspberry Pi 4B Flipper Zero development helper. "
                      "Explain safe steps. Never claim you performed local commands, "
                      "flashed firmware, or examined data beyond the supplied input. "
                      "Never suggest using ESP32 .bin images as a Flipper F7 updater."),
        input=prompt + context,
    )
    return response.output_text or "(No text returned)"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    for action in ("status", "usb", "firmware", "once"):
        commands.add_parser(action)
    watch = commands.add_parser("watch")
    watch.add_argument("--interval", type=int, default=30)
    app = commands.add_parser("approve")
    app.add_argument("number", type=int)
    ai = commands.add_parser("ask")
    ai.add_argument("question", nargs="?")
    ai.add_argument("--with-diagnostics", action="store_true")
    arguments = parser.parse_args()
    try:
        if arguments.action == "status":
            print(json.dumps(diagnostics(), indent=2))
        elif arguments.action == "usb":
            print(json.dumps(usb_status(), indent=2))
        elif arguments.action == "firmware":
            print(json.dumps(firmware_inventory(), indent=2))
        elif arguments.action == "once":
            poll_once()
        elif arguments.action == "watch":
            print("Pi watcher active. Private GitHub Issues only; "
                  "no remote shell and no flashing. Ctrl+C to stop.", flush=True)
            while True:
                try:
                    poll_once()
                except BridgeError as exc:
                    print("GitHub unavailable: " + redact(exc), flush=True)
                time.sleep(max(15, arguments.interval))
        elif arguments.action == "approve":
            approve(arguments.number)
        elif arguments.action == "ask":
            prompt = arguments.question or input("Ask the Pi AI assistant: ")
            print(ask(prompt, with_diagnostics=arguments.with_diagnostics))
        return 0
    except KeyboardInterrupt:
        return 130
    except (BridgeError, OSError, ValueError) as exc:
        print("STOP: " + redact(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
