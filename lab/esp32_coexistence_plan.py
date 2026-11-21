#!/usr/bin/env python3
"""Offline, fail-closed ESP32/ESP32-S2 shared-backpack planning gate.

Only reads local JSON; does not import serial/GPIO/network libraries or operate hardware.
This is a planning filter, NOT electrical approval.
"""
import argparse
import json
import sys

FAMILIES = {"esp32", "esp32-s2"}
ALLOWED_TRANSPORTS = {"usb", "uart", "ble", "wifi"}
MAX_DEVICES = 8

def inspect(plan):
    issues = []
    if not isinstance(plan, dict) or set(plan) != {"devices", "shared_power", "shared_gpio"}:
        return ["schema: expected devices, shared_power, shared_gpio"]
    devices = plan["devices"]
    if not isinstance(devices, list) or not 1 <= len(devices) <= MAX_DEVICES:
        return ["devices: expected 1-8 devices"]
    seen = set()
    for index, dev in enumerate(devices):
        p = f"devices[{index}]"
        if not isinstance(dev, dict) or set(dev) != {"id", "family", "transport", "board_verified"}:
            issues.append(p + ": invalid schema")
            continue
        name, family, transport, verified = (dev[k] for k in ("id", "family", "transport", "board_verified"))
        if not isinstance(name, str) or not name.isascii() or not name.replace("-", "").replace("_", "").isalnum() or len(name) > 32:
            issues.append(p + ": invalid id")
        elif name in seen:
            issues.append(p + ": duplicate id")
        else:
            seen.add(name)
        if family not in FAMILIES:
            issues.append(p + ": unsupported chip family")
        if transport not in ALLOWED_TRANSPORTS:
            issues.append(p + ": unsupported transport")
        if type(verified) is not bool or not verified:
            issues.append(p + ": board pinout/identity not independently verified")
        if family == "esp32-s2" and transport == "ble":
            issues.append(p + ": ESP32-S2 has no native Bluetooth/BLE radio")
    if plan["shared_power"] is not False:
        issues.append("shared_power: must be false pending independent supply/backfeed review")
    if plan["shared_gpio"] is not False:
        issues.append("shared_gpio: must be false pending voltage and pinout review")
    return issues

def selftest():
    base = {"devices":[{"id":"wroom", "family":"esp32", "transport":"usb", "board_verified":True}],
            "shared_power":False, "shared_gpio":False}
    def test(change, expected):
        obj = json.loads(json.dumps(base))
        change(obj)
        got = inspect(obj)
        assert (len(got) == 0) == expected, got
    test(lambda p: None, True)
    test(lambda p: p["devices"].append({"id":"s2","family":"esp32-s2","transport":"usb","board_verified":True}), True)
    test(lambda p: p["devices"][0].update(transport="ble"), True)
    test(lambda p: p["devices"][0].update(family="esp32-s2", transport="ble"), False)
    test(lambda p: p.update(shared_power=True), False)
    test(lambda p: p.update(shared_gpio=True), False)
    test(lambda p: p["devices"][0].update(board_verified=False), False)
    test(lambda p: p["devices"].append(dict(p["devices"][0])), False)
    test(lambda p: p["devices"][0].update(family="unknown"), False)
    test(lambda p: p["devices"][0].update(transport="uart"), True)
    print("10 offline synthetic tests passed")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", nargs="?", help="local public-safe JSON plan")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        selftest()
        return 0
    if not args.fixture:
        parser.error("supply fixture or --self-test")
    try:
        with open(args.fixture, "r", encoding="utf-8") as stream:
            plan = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: invalid/unreadable local plan ({type(exc).__name__})")
        return 2
    issues = inspect(plan)
    if issues:
        for issue in issues:
            print("BLOCKED:", issue)
        return 2
    print("PLAN CHECK ONLY: no detected schema/transport conflicts; NOT approved for wiring or flashing")
    return 0

if __name__ == "__main__":
    sys.exit(main())
