#!/usr/bin/env python3
"""Offline ESP32-WROOM boot-mode plan validator. No serial/network/GPIO access."""
import argparse
import json
import sys

ALLOWED = {"esp32-wroom-32", "esp32-s2"}
def validate(plan):
    if not isinstance(plan, dict):
        return ["plan must be an object"]
    errors = []
    if plan.get("board") not in ALLOWED:
        errors.append("board must be esp32-wroom-32 or esp32-s2")
    if plan.get("transport") != "usb-uart-owner-operated":
        errors.append("only owner-operated USB-UART plans are accepted")
    if plan.get("logic_voltage_v") != 3.3 or type(plan.get("logic_voltage_v")) not in (float, int):
        errors.append("logic voltage must be numeric 3.3V")
    if plan.get("common_ground_verified") is not True:
        errors.append("common ground must be explicitly verified")
    if plan.get("tx_rx_crossed_verified") is not True:
        errors.append("TX/RX crossover must be explicitly verified")
    if plan.get("power_source_verified") is not True:
        errors.append("power source must be verified")
    if plan.get("gpio0_at_reset") != "low":
        errors.append("GPIO0/BOOT must be low when EN reset is released for download mode")
    if plan.get("en_sequence") != ["low", "high"]:
        errors.append("EN reset sequence must be low then high")
    if plan.get("gpio0_after_reset") != "released":
        errors.append("BOOT must be released after reset")
    if plan.get("flash_requested") is not False:
        errors.append("offline diagnostic cannot authorize flashing")
    if plan.get("remote_control") is not False:
        errors.append("remote hardware control forbidden")
    if plan.get("board") == "esp32-s2" and plan.get("s2_usb_mode_confirmed") is not True:
        errors.append("ESP32-S2 USB/serial mode requires separate verification")
    return errors

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", nargs="?", help="local JSON plan; no hardware opened")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    sample = dict(board="esp32-wroom-32", transport="usb-uart-owner-operated",
                  logic_voltage_v=3.3, common_ground_verified=True,
                  tx_rx_crossed_verified=True, power_source_verified=True,
                  gpio0_at_reset="low", en_sequence=["low", "high"],
                  gpio0_after_reset="released", flash_requested=False,
                  remote_control=False)
    if args.self_test:
        assert validate(sample) == []
        for change in ({"logic_voltage_v": 5}, {"gpio0_at_reset": "high"},
                       {"en_sequence": ["high", "low"]}, {"flash_requested": True},
                       {"common_ground_verified": False}, {"remote_control": True},
                       {"transport": "network"}, {"board": "esp32-s2"}):
            assert validate({**sample, **change}), change
        assert validate([]) and validate({})
        print("PASS: 10 offline synthetic scenarios; no device access")
        return 0
    if not args.plan:
        parser.error("provide a local JSON file or --self-test")
    with open(args.plan, encoding="utf-8") as f:
        plan = json.load(f)
    problems = validate(plan)
    print(json.dumps({"accepted_for_manual_review": not problems,
                      "errors": problems,
                      "hardware_access": False}, indent=2))
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
