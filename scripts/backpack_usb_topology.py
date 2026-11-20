#!/usr/bin/env python3
"""Offline, fail-closed USB power-topology review. Never probes hardware.

Input: JSON object with 'nodes' [{id, kind, powered}] and 'links'
[{a,b,kind,backfeed_blocked}]. Only documented isolators/hubs may be
declared backfeed_blocked; this field is a claim to verify physically.
"""
import json
import sys

POWER = {"supply", "usb_host", "battery"}
KINDS = POWER | {"device", "isolator", "hub"}

def review(data):
    if not isinstance(data, dict) or not isinstance(data.get("nodes"), list) or not isinstance(data.get("links"), list):
        return ["invalid topology document"]
    nodes = {}
    errors = []
    for n in data["nodes"]:
        if not isinstance(n, dict) or not isinstance(n.get("id"), str) or not n["id"] or n.get("kind") not in KINDS or type(n.get("powered")) is not bool:
            errors.append("invalid node")
            continue
        if n["id"] in nodes:
            errors.append("duplicate node")
        nodes[n["id"]] = n
    for l in data["links"]:
        if not isinstance(l, dict) or l.get("kind") not in ("usb", "signal") or type(l.get("backfeed_blocked")) is not bool:
            errors.append("invalid link")
            continue
        a, b = l.get("a"), l.get("b")
        if a not in nodes or b not in nodes or a == b:
            errors.append("unknown or self-linked node")
            continue
        if l["kind"] == "usb" and not l["backfeed_blocked"] and nodes[a]["powered"] and nodes[b]["powered"]:
            errors.append("possible USB VBUS backfeed: " + a + " <-> " + b)
        if l["kind"] == "usb" and l["backfeed_blocked"]:
            errors.append("isolation claim requires manufacturer and meter verification: " + a + " <-> " + b)
    if not nodes:
        errors.append("no nodes")
    return errors or ["review only: no physical wiring approval"]

def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, UnicodeError):
        print("BLOCKED: invalid JSON")
        return 2
    findings = review(data)
    for finding in findings:
        print("BLOCKED: " + finding if finding != "review only: no physical wiring approval" else "REVIEW: " + finding)
    return 0 if findings == ["review only: no physical wiring approval"] else 2

if __name__ == "__main__":
    sys.exit(main())
