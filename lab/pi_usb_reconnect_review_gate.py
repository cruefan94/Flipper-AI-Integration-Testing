"""Offline, public-safe Pi USB reconnect review gate. No hardware access."""
import unittest

ROLES = {"flipper", "esp32-wroom", "esp32-s2"}
FIELDS = ("port", "vid", "pid", "serial", "role")

def normalize(snapshot):
    if not isinstance(snapshot, list):
        raise ValueError("not a list")
    ports, identities, out = set(), set(), {}
    for d in snapshot:
        if not isinstance(d, dict) or any(not isinstance(d.get(k), str) or not d[k].strip() for k in FIELDS):
            raise ValueError("missing identity")
        port, vid, pid, serial, role = (d[k].strip() for k in FIELDS)
        if not port.startswith("/dev/serial/by-id/") or ".." in port:
            raise ValueError("unstable port")
        if role not in ROLES or any(len(v) != 4 or any(c not in "0123456789abcdefABCDEF" for c in v) for v in (vid, pid)):
            raise ValueError("invalid USB ID or role")
        identity = (vid.lower(), pid.lower(), serial, role)
        if port in ports or identity in identities:
            raise ValueError("duplicate identity")
        ports.add(port)
        identities.add(identity)
        out.setdefault(role, []).append((port, identity))
    return out

def assess(before, after, intended_role):
    """Review status only: never grants flashing permission."""
    try:
        a, b = normalize(before), normalize(after)
        if intended_role not in ROLES:
            return "BLOCKED_INVALID_ROLE"
        if len(a.get(intended_role, [])) != 1 or len(b.get(intended_role, [])) != 1:
            return "BLOCKED_MISSING_OR_AMBIGUOUS"
        return "STABLE_REVIEW_ONLY" if a == b else "BLOCKED_TOPOLOGY_CHANGED"
    except ValueError:
        return "BLOCKED_INVALID_SNAPSHOT"

def device(role="esp32-wroom", serial="ABC", suffix="usb-A"):
    return {"role": role, "serial": serial, "vid": "10C4", "pid": "EA60", "port": "/dev/serial/by-id/" + suffix}

class GateTests(unittest.TestCase):
    def test_stable(self):
        x = [device()]
        self.assertEqual(assess(x, x, "esp32-wroom"), "STABLE_REVIEW_ONLY")
    def test_port_changed(self):
        self.assertEqual(assess([device()], [device(suffix="usb-B")], "esp32-wroom"), "BLOCKED_TOPOLOGY_CHANGED")
    def test_serial_changed(self):
        self.assertEqual(assess([device()], [device(serial="DEF")], "esp32-wroom"), "BLOCKED_TOPOLOGY_CHANGED")
    def test_missing(self):
        self.assertEqual(assess([device("esp32-s2")], [], "esp32-s2"), "BLOCKED_MISSING_OR_AMBIGUOUS")
    def test_duplicate_port(self):
        x = [device(), device("flipper", "DEF")]
        self.assertEqual(assess(x, x, "esp32-wroom"), "BLOCKED_INVALID_SNAPSHOT")
    def test_duplicate_identity(self):
        x = [device(), device(suffix="usb-B")]
        self.assertEqual(assess(x, x, "esp32-wroom"), "BLOCKED_INVALID_SNAPSHOT")
    def test_unstable_port(self):
        x = [device()]
        x[0]["port"] = "/dev/ttyUSB0"
        self.assertEqual(assess(x, x, "esp32-wroom"), "BLOCKED_INVALID_SNAPSHOT")
    def test_other_device_changed(self):
        x = [device(), device("flipper", "DEF", "usb-B")]
        self.assertEqual(assess(x, x[:1], "esp32-wroom"), "BLOCKED_TOPOLOGY_CHANGED")
    def test_unknown_role(self):
        x = [device()]
        self.assertEqual(assess(x, x, "unknown"), "BLOCKED_INVALID_ROLE")
    def test_bad_vid(self):
        x = [device()]
        x[0]["vid"] = "ZZZZ"
        self.assertEqual(assess(x, x, "esp32-wroom"), "BLOCKED_INVALID_SNAPSHOT")

if __name__ == "__main__":
    unittest.main()
