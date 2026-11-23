#!/usr/bin/env python3
"""Offline audit of operator-supplied Raspberry Pi serial observations.

No device enumeration, GPIO, serial access, flashing, or subprocess execution.
Input: JSON with a 'boards' list of {label, port, vid, pid, chip}.
USB VID/PID are not proof of the attached ESP chip.
"""
import argparse
import json
import re
import sys

PORT = re.compile(r"^/dev/(?:ttyUSB|ttyACM)(?:0|[1-9][0-9]{0,2})$")
HEX = re.compile(r"^[0-9A-Fa-f]{4}$")
CHIPS = {"esp32", "esp32-s2", "unknown"}


def audit(payload):
    if not isinstance(payload, dict) or set(payload) != {"boards"}:
        raise ValueError("expected only a boards array")
    boards = payload["boards"]
    if not isinstance(boards, list) or not 1 <= len(boards) <= 8:
        raise ValueError("boards must contain 1-8 records")
    ports, labels, findings = set(), set(), []
    for index, board in enumerate(boards):
        if not isinstance(board, dict) or set(board) != {"label", "port", "vid", "pid", "chip"}:
            raise ValueError(f"record {index}: expected label, port, vid, pid, chip")
        label, port, vid, pid, chip = (board[k] for k in ("label", "port", "vid", "pid", "chip"))
        if not isinstance(label, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,31}", label):
            raise ValueError(f"record {index}: invalid label")
        if not isinstance(port, str) or not PORT.fullmatch(port):
            raise ValueError(f"record {index}: invalid canonical Linux serial port")
        if not isinstance(vid, str) or not HEX.fullmatch(vid) or not isinstance(pid, str) or not HEX.fullmatch(pid):
            raise ValueError(f"record {index}: VID/PID must be four hexadecimal digits each")
        if not isinstance(chip, str) or chip not in CHIPS:
            raise ValueError(f"record {index}: unsupported chip observation")
        if label.casefold() in labels or port in ports:
            raise ValueError(f"record {index}: duplicate label or port")
        labels.add(label.casefold())
        ports.add(port)
        findings.append({"label": label, "port": port, "usb_id": f"{vid.upper()}:{pid.upper()}",
                         "chip_claim": chip, "verified_chip": False})
    return {"safe_to_flash": False, "hardware_accessed": False, "observations": findings,
            "warning": "USB bridge IDs do not verify ESP32 chip identity; confirm on physical board."}


def self_test():
    import unittest
    class Tests(unittest.TestCase):
        def setUp(self):
            self.b = {"label": "WROOM", "port": "/dev/ttyUSB0", "vid": "10c4",
                      "pid": "ea60", "chip": "esp32"}
        def check_bad(self, key, value):
            item = dict(self.b, **{key: value})
            with self.assertRaises(ValueError):
                audit({"boards": [item]})
        def test_valid(self):
            self.assertFalse(audit({"boards": [self.b]})["safe_to_flash"])
        def test_duplicate_port(self):
            with self.assertRaises(ValueError):
                audit({"boards": [self.b, dict(self.b, label="S2")]})
        def test_duplicate_label_casefold(self):
            with self.assertRaises(ValueError):
                audit({"boards": [self.b, dict(self.b, label="wroom", port="/dev/ttyACM0")]})
        def test_alias(self):
            self.check_bad("port", "/dev/ttyUSB00")
        def test_windows_port(self):
            self.check_bad("port", "COM3")
        def test_path_traversal(self):
            self.check_bad("port", "/dev/../ttyUSB0")
        def test_bad_usb_id(self):
            self.check_bad("vid", "0x10c4")
        def test_chip_claim_not_verified(self):
            self.assertFalse(audit({"boards": [self.b]})["observations"][0]["verified_chip"])
        def test_empty(self):
            with self.assertRaises(ValueError):
                audit({"boards": []})
        def test_extra_fields(self):
            with self.assertRaises(ValueError):
                audit({"boards": [dict(self.b, authorize_flash=True)]})
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("input", nargs="?", help="operator-authored JSON fixture (not a device)")
    args = parser.parse_args()
    if args.self_test:
        return 0 if self_test() else 1
    if not args.input:
        parser.error("provide a JSON fixture path or --self-test")
    try:
        with open(args.input, "rb") as stream:
            raw = stream.read(16385)
        if len(raw) > 16384:
            raise ValueError("fixture exceeds 16 KiB")
        data = json.loads(raw.decode("utf-8"))
        print(json.dumps(audit(data), indent=2, sort_keys=True))
        return 0
    except (ValueError, UnicodeError, OSError) as exc:
        print(f"INVALID OFFLINE OBSERVATION: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
