"""Offline, advisory-only ESP32 preflight. No hardware imports or side effects."""
import json
import re
import sys

CHIPS = {"esp32", "esp32-s2"}
PORT = re.compile(r"(?:/dev/tty(?:USB|ACM)[0-9]+|COM[1-9][0-9]*)\Z", re.I)

def evaluate(record):
    if not isinstance(record, dict) or set(record) != {"chip", "port", "boot_log", "wiring_checked", "owner_authorized"}:
        return {"ready": False, "reason": "invalid-schema"}
    chip, port, log = record["chip"], record["port"], record["boot_log"]
    if not isinstance(chip, str) or chip not in CHIPS:
        return {"ready": False, "reason": "unknown-chip"}
    if not isinstance(port, str) or not PORT.fullmatch(port) or len(port) > 64:
        return {"ready": False, "reason": "invalid-port"}
    if not isinstance(log, str) or len(log) > 4096:
        return {"ready": False, "reason": "invalid-log"}
    if record["wiring_checked"] is not True or record["owner_authorized"] is not True:
        return {"ready": False, "reason": "missing-safety-confirmation"}
    return {"ready": False, "reason": "physical-verification-required", "candidate_chip": chip, "candidate_port": port}

def main():
    try:
        raw = sys.stdin.read(8193)
        if len(raw) > 8192:
            raise ValueError("input-too-large")
        result = evaluate(json.loads(raw))
    except (ValueError, UnicodeError):
        result = {"ready": False, "reason": "invalid-input"}
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
