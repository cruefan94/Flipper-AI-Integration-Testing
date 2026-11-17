"""Offline-only Pi serial ownership arbitration for Flipper/ESP32 coexistence.

No serial opening, subprocesses, USB probing or hardware writes.
"""
from dataclasses import dataclass
from pathlib import PurePosixPath
import re

SAFE_PORT = re.compile(r"^/dev/(ttyUSB[0-9]+|ttyACM[0-9]+)$")
ALLOWED = frozenset({"flipper", "esp32-wroom", "esp32-s2", "unknown"})

@dataclass(frozen=True)
class Observation:
    port: str
    device: str
    owner: str
    verified: bool

def assess(observations, requested_port, requested_device):
    """Return (allowed_for_offline_review, reason); never grants hardware access."""
    if not isinstance(requested_port, str) or not SAFE_PORT.fullmatch(requested_port):
        return False, "invalid-port"
    if requested_device not in ALLOWED or requested_device == "unknown":
        return False, "unknown-requested-device"
    if not observations:
        return False, "missing-observations"
    if any(not isinstance(o, Observation) for o in observations):
        return False, "invalid-observation"
    if any(not isinstance(o.port, str) or not SAFE_PORT.fullmatch(o.port)
           or o.device not in ALLOWED or not isinstance(o.owner, str)
           or not o.owner.strip() for o in observations):
        return False, "invalid-observation"
    matches = [o for o in observations if o.port == requested_port]
    if not matches:
        return False, "port-not-observed"
    if any(not o.verified for o in matches):
        return False, "identity-unverified"
    if len({(o.device, o.owner) for o in matches}) != 1:
        return False, "conflicting-port-claims"
    match = matches[0]
    if match.device != requested_device:
        return False, "wrong-device"
    if match.owner != "idle":
        return False, "port-in-use"
    return True, "offline-review-only"

if __name__ == "__main__":
    import unittest

    class Cases(unittest.TestCase):
        def setUp(self):
            self.ok = [Observation("/dev/ttyUSB0", "esp32-wroom", "idle", True)]
        def test_idle(self): self.assertEqual(assess(self.ok, "/dev/ttyUSB0", "esp32-wroom"), (True, "offline-review-only"))
        def test_qflipper_claim(self): self.assertEqual(assess([Observation("/dev/ttyACM0", "flipper", "qFlipper", True)], "/dev/ttyACM0", "flipper")[1], "port-in-use")
        def test_wrong_device(self): self.assertEqual(assess(self.ok, "/dev/ttyUSB0", "esp32-s2")[1], "wrong-device")
        def test_unverified(self): self.assertEqual(assess([Observation("/dev/ttyUSB0", "esp32-wroom", "idle", False)], "/dev/ttyUSB0", "esp32-wroom")[1], "identity-unverified")
        def test_conflict(self): self.assertEqual(assess(self.ok + [Observation("/dev/ttyUSB0", "flipper", "idle", True)], "/dev/ttyUSB0", "esp32-wroom")[1], "conflicting-port-claims")
        def test_missing(self): self.assertEqual(assess([], "/dev/ttyUSB0", "esp32-wroom")[1], "missing-observations")
        def test_path_injection(self): self.assertEqual(assess(self.ok, "/dev/ttyUSB0/../../etc/passwd", "esp32-wroom")[1], "invalid-port")
        def test_unknown(self): self.assertEqual(assess(self.ok, "/dev/ttyUSB0", "unknown")[1], "unknown-requested-device")
        def test_no_port(self): self.assertEqual(assess(self.ok, "/dev/ttyACM0", "flipper")[1], "port-not-observed")
        def test_bad_observation(self): self.assertEqual(assess(["ttyUSB0"], "/dev/ttyUSB0", "esp32-wroom")[1], "invalid-observation")
    unittest.main()
