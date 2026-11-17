"""Public-safe offline USB snapshot preflight. No device access or flashing."""
import json
import re
import sys
import unittest

PORT = re.compile(r"^/dev/(ttyUSB|ttyACM)[0-9]+$")
HEX4 = re.compile(r"^[0-9a-fA-F]{4}$")
ALLOWED = {"flipper", "esp32-wroom", "esp32-s2", "arduino-uno"}


def review(snapshot):
    """Fail closed on incomplete or ambiguous recorded USB identities."""
    if not isinstance(snapshot, list) or not snapshot:
        return {"status": "BLOCKED", "reasons": ["empty_or_invalid_snapshot"]}
    reasons, ports, identities = [], set(), set()
    for i, entry in enumerate(snapshot):
        if not isinstance(entry, dict):
            reasons.append(f"row_{i}_invalid")
            continue
        port, kind = entry.get("port"), entry.get("kind")
        vid, pid, serial = entry.get("vid"), entry.get("pid"), entry.get("serial")
        if not isinstance(port, str) or not PORT.fullmatch(port):
            reasons.append(f"row_{i}_invalid_port")
        elif port in ports:
            reasons.append(f"row_{i}_duplicate_port")
        else:
            ports.add(port)
        if kind not in ALLOWED:
            reasons.append(f"row_{i}_unknown_kind")
        if not all(isinstance(x, str) and HEX4.fullmatch(x) for x in (vid, pid)):
            reasons.append(f"row_{i}_invalid_vid_pid")
        if not isinstance(serial, str) or not serial.strip() or len(serial) > 128:
            reasons.append(f"row_{i}_missing_serial")
        else:
            identity = (str(vid).lower(), str(pid).lower(), serial)
            if identity in identities:
                reasons.append(f"row_{i}_duplicate_identity")
            identities.add(identity)
    return {"status": "REVIEW_ONLY" if not reasons else "BLOCKED", "reasons": reasons}


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.good = {"port": "/dev/ttyUSB0", "kind": "esp32-wroom", "vid": "10c4", "pid": "ea60", "serial": "FIXTURE-A"}

    def test_valid_review_only(self):
        self.assertEqual(review([self.good])["status"], "REVIEW_ONLY")

    def test_empty(self):
        self.assertEqual(review([])["status"], "BLOCKED")

    def test_invalid_port(self):
        self.assertEqual(review([{**self.good, "port": "/dev/sda"}])["status"], "BLOCKED")

    def test_duplicate_port(self):
        self.assertEqual(review([self.good, {**self.good, "serial": "FIXTURE-B"}])["status"], "BLOCKED")

    def test_duplicate_identity(self):
        self.assertEqual(review([self.good, {**self.good, "port": "/dev/ttyUSB1"}])["status"], "BLOCKED")

    def test_missing_serial(self):
        self.assertEqual(review([{**self.good, "serial": ""}])["status"], "BLOCKED")

    def test_bad_vid(self):
        self.assertEqual(review([{**self.good, "vid": "ZZZZ"}])["status"], "BLOCKED")

    def test_unknown_board(self):
        self.assertEqual(review([{**self.good, "kind": "unknown"}])["status"], "BLOCKED")

    def test_non_dictionary(self):
        self.assertEqual(review([None])["status"], "BLOCKED")

    def test_two_boards(self):
        second = {**self.good, "port": "/dev/ttyACM0", "kind": "flipper", "vid": "0483", "pid": "5740", "serial": "FIXTURE-B"}
        self.assertEqual(review([self.good, second])["status"], "REVIEW_ONLY")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 1:
        try:
            result = review(json.load(sys.stdin))
            print(json.dumps(result, sort_keys=True))
            sys.exit(0 if result["status"] == "REVIEW_ONLY" else 2)
        except (ValueError, TypeError):
            print(json.dumps({"status": "BLOCKED", "reasons": ["invalid_json"]}))
            sys.exit(2)
    else:
        sys.exit("Usage: python pi_usb_snapshot_contract.py [--self-test] < snapshot.json")
