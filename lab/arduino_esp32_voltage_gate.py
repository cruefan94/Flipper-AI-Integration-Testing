#!/usr/bin/env python3
"""Offline Arduino Uno / ESP32 / Flipper GPIO voltage compatibility gate.

No hardware access, network calls, flashing, or authorization of wiring.
Input is a public-safe JSON description, not measured hardware state.
"""
import argparse
import json
import sys

MAX_BYTES = 16384
ALLOWED = {"arduino_uno", "esp32_wroom", "esp32_s2", "flipper_zero", "raspberry_pi_4b"}
LOGIC = {"arduino_uno": 5.0, "esp32_wroom": 3.3, "esp32_s2": 3.3,
         "flipper_zero": 3.3, "raspberry_pi_4b": 3.3}


def evaluate(data):
    if not isinstance(data, dict) or set(data) != {"source", "target", "signal", "converter"}:
        raise ValueError("expected source, target, signal, converter only")
    source, target = data["source"], data["target"]
    if not isinstance(source, str) or not isinstance(target, str) or source not in ALLOWED or target not in ALLOWED:
        raise ValueError("unknown board")
    if data["signal"] not in ("gpio", "uart"):
        raise ValueError("only gpio and uart are evaluated")
    if type(data["converter"]) is not bool:
        raise ValueError("converter must be boolean")
    if source == target:
        return {"decision": "REVIEW", "reason": "Same-board wiring is not automatically approved"}
    if LOGIC[source] > LOGIC[target]:
        return {"decision": "REVIEW" if data["converter"] else "BLOCK",
                "reason": "5V output to 3.3V input requires verified level shifting and shared-ground review"}
    return {"decision": "REVIEW", "reason": "Nominal logic levels alone cannot validate pin function, supply, or ground"}


def self_test():
    cases = [
        ({"source":"arduino_uno","target":"esp32_wroom","signal":"uart","converter":False},"BLOCK"),
        ({"source":"arduino_uno","target":"flipper_zero","signal":"gpio","converter":False},"BLOCK"),
        ({"source":"arduino_uno","target":"raspberry_pi_4b","signal":"uart","converter":True},"REVIEW"),
        ({"source":"esp32_s2","target":"arduino_uno","signal":"uart","converter":False},"REVIEW"),
        ({"source":"esp32_wroom","target":"flipper_zero","signal":"gpio","converter":False},"REVIEW"),
    ]
    for case, expected in cases:
        assert evaluate(case)["decision"] == expected
    for bad in ({}, {"source":"arduino_uno","target":"esp32_s2","signal":"spi","converter":False},
                {"source":"arduino_uno","target":"esp32_s2","signal":"uart","converter":"yes"}):
        try:
            evaluate(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid fixture accepted")
    print("8/8 offline synthetic cases passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", nargs="?", help="public-safe JSON fixture file")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.fixture:
        parser.error("fixture required unless --self-test")
    with open(args.fixture, "rb") as f:
        raw = f.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("fixture exceeds 16 KiB")
    print(json.dumps(evaluate(json.loads(raw.decode("utf-8"))), sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print("INVALID: " + str(exc), file=sys.stderr)
        sys.exit(2)
