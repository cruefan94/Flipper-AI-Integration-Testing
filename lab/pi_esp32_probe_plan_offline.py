#!/usr/bin/env python3
"""Offline-only Raspberry Pi ESP32 probe-plan validator. Never opens a port."""
import argparse
import json
import re
import sys

CHIPS = {"esp32", "esp32s2"}
BY_ID = re.compile(r"^/dev/serial/by-id/[A-Za-z0-9_.:+-]+$")
SERIAL = re.compile(r"^[A-Za-z0-9_.:+-]{8,200}$")

def validate(record):
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    required = {"chip", "port", "usb_identity", "identity_stable", "voltage_verified",
                "common_ground_verified", "owner_authorized", "rom_download_mode"}
    if set(record) != required:
        raise ValueError("unexpected or missing fields")
    chip = record["chip"]
    port = record["port"]
    identity = record["usb_identity"]
    if type(chip) is not str or chip not in CHIPS:
        raise ValueError("unsupported chip")
    if type(port) is not str or not BY_ID.fullmatch(port) or ".." in port:
        raise ValueError("requires a stable /dev/serial/by-id device path")
    if type(identity) is not str or not SERIAL.fullmatch(identity) or identity not in port:
        raise ValueError("USB identity must match stable device path")
    for flag in ("identity_stable", "voltage_verified", "common_ground_verified",
                 "owner_authorized", "rom_download_mode"):
        if record[flag] is not True:
            raise ValueError(flag + " must be explicitly true")
    # Informational only; NEVER execute this command here.
    return ["python3", "-m", "esptool", "--chip", chip, "--port", port, "read_mac"]

def selftest():
    base = dict(chip="esp32", port="/dev/serial/by-id/usb-CP2102_A1234",
                usb_identity="CP2102_A1234", identity_stable=True,
                voltage_verified=True, common_ground_verified=True,
                owner_authorized=True, rom_download_mode=True)
    assert validate(base)[-1] == "read_mac"
    alt = dict(base, chip="esp32s2")
    assert validate(alt)[4] == "esp32s2"
    cases = [
        dict(base, chip="esp32c3"), dict(base, port="/dev/ttyUSB0"),
        dict(base, port="/dev/serial/by-id/../../ttyUSB0"),
        dict(base, usb_identity="OTHER"), dict(base, identity_stable=False),
        dict(base, voltage_verified=False), dict(base, common_ground_verified=False),
        dict(base, owner_authorized=False), dict(base, rom_download_mode=False),
        dict(base, owner_authorized=1), dict(base, unexpected=True),
        dict(base, port="/dev/serial/by-id/usb-CP2102_A1234;echo"),
    ]
    for item in cases:
        try:
            validate(item)
        except ValueError:
            pass
        else:
            raise AssertionError("unsafe record accepted: " + repr(item))
    print("14/14 offline tests passed")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        selftest()
        return 0
    if not args.json_file:
        parser.error("provide a JSON file or --self-test")
    try:
        with open(args.json_file, encoding="utf-8") as file:
            record = json.load(file)
        print(json.dumps({"status": "PLAN_ONLY_NOT_EXECUTED", "argv": validate(record)}))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
