"""First-generation Pironman settings preview ONLY.

Pure data validation and reversible before/after plan. No hardware or system I/O.
Does not assume which Pironman daemon/API is installed.
"""
from dataclasses import dataclass
import unittest

RGB = frozenset(("UNCHANGED", "OFF", "STATIC"))
OLED = frozenset(("UNCHANGED", "ON", "OFF"))
FAN = frozenset(("UNCHANGED", "AUTO"))


@dataclass(frozen=True)
class PironmanSettings:
    rgb: str = "UNCHANGED"
    oled: str = "UNCHANGED"
    fan: str = "UNCHANGED"


def _validate(value):
    if type(value) is not PironmanSettings:
        raise ValueError("invalid settings")
    for field, allowed in (("rgb", RGB), ("oled", OLED), ("fan", FAN)):
        if type(getattr(value, field)) is not str or getattr(value, field) not in allowed:
            raise ValueError("unsupported setting")
    return value


def preview(current, requested):
    """Return an immutable preview and explicit rollback, never apply changes.

    UNCHANGED is a sentinel, not a claim about the current physical state.
    A rollback is a *plan*, requiring a later hardware-specific implementation
    and actual captured settings before any device writes are considered.
    """
    current, requested = _validate(current), _validate(requested)
    target = PironmanSettings(**{
        name: getattr(current, name) if getattr(requested, name) == "UNCHANGED"
        else getattr(requested, name)
        for name in ("rgb", "oled", "fan")
    })
    return {"before": current, "proposed": target, "rollback": current,
            "applied": False, "hardware_verified": False}


class SettingsPreviewTests(unittest.TestCase):
    def test_no_change(self):
        p = preview(PironmanSettings(), PironmanSettings())
        self.assertEqual(p["before"], p["proposed"])
        self.assertFalse(p["applied"])

    def test_preview_and_rollback(self):
        before = PironmanSettings(rgb="STATIC", oled="ON", fan="AUTO")
        p = preview(before, PironmanSettings(rgb="OFF", oled="OFF"))
        self.assertEqual(p["proposed"], PironmanSettings(rgb="OFF", oled="OFF", fan="AUTO"))
        self.assertEqual(p["rollback"], before)

    def test_fan_cannot_be_disabled(self):
        with self.assertRaises(ValueError):
            preview(PironmanSettings(), PironmanSettings(fan="OFF"))

    def test_reject_arbitrary_rgb(self):
        with self.assertRaises(ValueError):
            preview(PironmanSettings(), PironmanSettings(rgb="EXECUTE"))

    def test_reject_unverified_brightness(self):
        with self.assertRaises(ValueError):
            preview(PironmanSettings(), {"brightness": 100})

    def test_reject_injected_oled(self):
        with self.assertRaises(ValueError):
            preview(PironmanSettings(), PironmanSettings(oled="ON\\nTOKEN"))

    def test_immutable(self):
        from dataclasses import FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            PironmanSettings().fan = "OFF"

    def test_no_io_dependencies(self):
        import inspect
        src = inspect.getsource(preview)
        for token in ("subprocess", "os.system", "open(", "requests.", "serial.", "gpio"):
            self.assertNotIn(token, src)


if __name__ == "__main__":
    unittest.main()
