"""Offline USB identity drift guard. No device access or flashing."""
import json
import re
import sys

PORT = re.compile(r"^/dev/(ttyUSB|ttyACM)[0-9]+$")
HEX4 = re.compile(r"^[0-9a-fA-F]{4}$")

def normalize(snapshot):
    if not isinstance(snapshot, list):
        raise ValueError("snapshot must be a list")
    result, identities = {}, set()
    for entry in snapshot:
        if not isinstance(entry, dict):
            raise ValueError("entry must be an object")
        port, vid, pid, serial = (entry.get(k) for k in ("port", "vid", "pid", "serial"))
        if not isinstance(port, str) or not PORT.fullmatch(port):
            raise ValueError("invalid port")
        if not isinstance(vid, str) or not HEX4.fullmatch(vid) or not isinstance(pid, str) or not HEX4.fullmatch(pid):
            raise ValueError("invalid USB VID/PID")
        if not isinstance(serial, str) or not serial.strip() or len(serial) > 128:
            raise ValueError("missing/invalid serial identity")
        identity = (vid.lower(), pid.lower(), serial)
        if port in result or identity in identities:
            raise ValueError("duplicate port or device identity")
        identities.add(identity)
        result[port] = identity
    return result

def compare(before, after):
    a, b = normalize(before), normalize(after)
    changes = []
    for port in sorted(set(a) | set(b)):
        if port not in a:
            changes.append({"port": port, "kind": "added"})
        elif port not in b:
            changes.append({"port": port, "kind": "removed"})
        elif a[port] != b[port]:
            changes.append({"port": port, "kind": "identity_changed"})
    return {"stable": not changes, "changes": changes, "flash_authorized": False}

def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: usb_topology_guard.py BEFORE.json AFTER.json")
    with open(sys.argv[1], encoding="utf-8") as f:
        before = json.load(f)
    with open(sys.argv[2], encoding="utf-8") as f:
        after = json.load(f)
    print(json.dumps(compare(before, after), sort_keys=True))

if __name__ == "__main__":
    main()
