"""Offline, read-only comparison of consented USB VID/PID inventory results.

Accepts JSON snapshots from usb_vidpid_inventory.py; never accesses hardware.
Do not interpret matching VID/PID as device identity or connectivity proof.
"""
from collections import Counter
import json
import re

HEX4 = re.compile(r"[0-9a-f]{4}\Z")

def _counts(snapshot):
    if not isinstance(snapshot, dict) or snapshot.get("status") != "read_only_inventory":
        raise ValueError("only authorized read_only_inventory snapshots are accepted")
    devices = snapshot.get("devices")
    if not isinstance(devices, list) or len(devices) > 256:
        raise ValueError("invalid or oversized device list")
    counts = Counter()
    for device in devices:
        if not isinstance(device, dict):
            raise ValueError("invalid device")
        vid, pid = device.get("vendor_id"), device.get("product_id")
        if not isinstance(vid, str) or not isinstance(pid, str) or not HEX4.fullmatch(vid) or not HEX4.fullmatch(pid):
            raise ValueError("invalid VID/PID")
        counts[(vid, pid)] += 1
    return counts

def compare(before, after):
    old, new = _counts(before), _counts(after)
    def rows(counter):
        return [{"vendor_id": vid, "product_id": pid, "count": count}
                for (vid, pid), count in sorted(counter.items()) if count > 0]
    return {"status": "offline_comparison", "added": rows(new - old),
            "removed": rows(old - new), "identity": "unverified",
            "usb_access": "not_tested", "backup": "not_tested", "recovery": "not_tested"}

def main():
    import argparse
    p = argparse.ArgumentParser(description="Compare two previously captured USB inventory JSON files offline")
    p.add_argument("before")
    p.add_argument("after")
    args = p.parse_args()
    # Never read live /sys or /dev; only user-supplied local JSON files.
    with open(args.before, encoding="utf-8") as f:
        before = json.load(f)
    with open(args.after, encoding="utf-8") as f:
        after = json.load(f)
    print(json.dumps(compare(before, after), sort_keys=True))

if __name__ == "__main__":
    main()
