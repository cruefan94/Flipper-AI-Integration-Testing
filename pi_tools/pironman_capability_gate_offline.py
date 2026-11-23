"""Offline first-generation Pironman capability gate; no hardware access.

Only owner-confirmed, non-sensitive capability evidence is accepted. This module
does not identify installed software or authorize applying settings.
"""
from dataclasses import dataclass
import unittest

CAPABILITIES = frozenset(("rgb", "oled", "fan_auto"))
STATUS = frozenset(("confirmed", "unknown", "unsupported"))


@dataclass(frozen=True)
class CapabilityEvidence:
    name: str
    status: str
    owner_confirmed: bool = False


def assess(evidence):
    """Return immutable readiness facts, never a hardware-control permission."""
    if type(evidence) not in (tuple, list):
        raise ValueError("evidence must be a sequence")
    seen = set()
    results = {}
    for entry in evidence:
        if type(entry) is not CapabilityEvidence:
            raise ValueError("invalid evidence")
        if (type(entry.name) is not str or entry.name not in CAPABILITIES
                or type(entry.status) is not str or entry.status not in STATUS
                or type(entry.owner_confirmed) is not bool):
            raise ValueError("invalid capability")
        if entry.name in seen:
            raise ValueError("duplicate capability")
        seen.add(entry.name)
        results[entry.name] = (entry.status == "confirmed" and entry.owner_confirmed)
    return {
        "ready_for_ui_preview": all(results.get(k, False) for k in CAPABILITIES),
        "verified_capabilities": tuple(sorted(k for k, v in results.items() if v)),
        "hardware_write_authorized": False,
        "device_tested": False,
    }


class GateTests(unittest.TestCase):
    def test_empty_fails_closed(self):
        self.assertFalse(assess(())["ready_for_ui_preview"])

    def test_all_confirmed_preview_only(self):
        e = tuple(CapabilityEvidence(k, "confirmed", True) for k in CAPABILITIES)
        result = assess(e)
        self.assertTrue(result["ready_for_ui_preview"])
        self.assertFalse(result["hardware_write_authorized"])
        self.assertFalse(result["device_tested"])

    def test_unconfirmed_fails_closed(self):
        e = tuple(CapabilityEvidence(k, "confirmed") for k in CAPABILITIES)
        self.assertFalse(assess(e)["ready_for_ui_preview"])

    def test_unknown_fails_closed(self):
        e = tuple(CapabilityEvidence(k, "unknown", True) for k in CAPABILITIES)
        self.assertFalse(assess(e)["ready_for_ui_preview"])

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            assess((CapabilityEvidence("rgb", "confirmed", True),) * 2)

    def test_unrecognized_rejected(self):
        with self.assertRaises(ValueError):
            assess((CapabilityEvidence("shell", "confirmed", True),))

    def test_type_rejected(self):
        with self.assertRaises(ValueError):
            assess(({"name": "rgb"},))

    def test_boolean_must_be_boolean(self):
        with self.assertRaises(ValueError):
            assess((CapabilityEvidence("rgb", "confirmed", 1),))


if __name__ == "__main__":
    unittest.main()
