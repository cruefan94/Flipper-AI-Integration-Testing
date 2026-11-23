"""Offline-only classification of owner-supplied Pironman unit-file evidence."""
import re
import unittest

KNOWN = ("pironman.service", "pironman5.service", "pironman-oled.service")
LINE = re.compile(r"^([a-zA-Z0-9_.@-]{1,80}\.service)\s+(enabled|disabled|static|masked|generated|indirect)$")

def summarize(evidence: str) -> tuple[str, ...]:
    if type(evidence) is not str or len(evidence) > 16384:
        raise ValueError("invalid evidence")
    found = {}
    for line in evidence.splitlines():
        match = LINE.fullmatch(line.strip())
        if match and match.group(1) in KNOWN:
            unit, state = match.groups()
            if unit in found:
                raise ValueError("duplicate unit")
            found[unit] = state
    return tuple(f"{unit}: {found.get(unit, 'NOT OBSERVED')}" for unit in KNOWN)

class Tests(unittest.TestCase):
    def test_observed(self):
        self.assertIn("pironman.service: enabled", summarize("pironman.service enabled"))
    def test_unknown(self):
        self.assertIn("pironman.service: NOT OBSERVED", summarize(""))
    def test_privacy(self):
        self.assertNotIn("secret", " ".join(summarize("secret.service enabled\nsecret token")))
    def test_duplicate(self):
        with self.assertRaises(ValueError):
            summarize("pironman.service enabled\npironman.service disabled")
    def test_bound(self):
        with self.assertRaises(ValueError):
            summarize("x" * 16385)
    def test_no_running_claim(self):
        self.assertNotIn("running", " ".join(summarize("pironman.service enabled")))

if __name__ == "__main__":
    unittest.main()
