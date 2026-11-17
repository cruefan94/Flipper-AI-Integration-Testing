"""Public-safe offline USB/serial identity contract. No hardware I/O."""
from collections import Counter
import re

SUPPORTED = {"flipper_zero", "esp32_wroom", "esp32_s2", "arduino_uno"}
PORT = re.compile(r"^/dev/(ttyACM|ttyUSB)[0-9]+$")
HEX4 = re.compile(r"^[0-9a-fA-F]{4}$")

def review(before, after, target):
    """Fail closed on USB drift, ambiguous identity, or missing provenance.

    Records: board, port, vid, pid, serial, topology. This is NOT a flash permit.
    """
    def validate(records):
        if not isinstance(records, list) or not records:
            return "missing snapshot"
        ports, identities, paths = [], [], []
        for d in records:
            if not isinstance(d, dict) or d.get("board") not in SUPPORTED:
                return "unsupported board"
            if not isinstance(d.get("port"), str) or not PORT.fullmatch(d["port"]):
                return "invalid port"
            if not all(isinstance(d.get(k), str) and HEX4.fullmatch(d[k])
                       for k in ("vid", "pid")):
                return "invalid USB IDs"
            if not all(isinstance(d.get(k), str) and d[k].strip()
                       for k in ("serial", "topology")):
                return "missing identity evidence"
            ports.append(d["port"])
            identities.append((d["vid"].lower(), d["pid"].lower(), d["serial"]))
            paths.append(d["topology"])
        if any(len(set(v)) != len(v) for v in (ports, identities, paths)):
            return "duplicate or conflicting identity"
        return None

    for snapshot in (before, after):
        reason = validate(snapshot)
        if reason:
            return {"review": "BLOCKED", "reason": reason, "flash_allowed": False}
    if not isinstance(target, str) or not target.strip():
        return {"review": "BLOCKED", "reason": "missing target serial", "flash_allowed": False}
    def keyed(records):
        return {d["serial"]: (d["board"], d["port"], d["vid"].lower(),
                              d["pid"].lower(), d["topology"]) for d in records}
    a, b = keyed(before), keyed(after)
    if target not in a or target not in b:
        reason = "target missing"
    elif a != b:
        reason = "USB identity or topology changed"
    else:
        reason = "stable offline snapshot; manual review only"
    return {"review": "REVIEW_ONLY" if a == b and target in a else "BLOCKED",
            "reason": reason, "flash_allowed": False}
