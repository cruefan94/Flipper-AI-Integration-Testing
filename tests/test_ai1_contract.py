"""Public-safe AI1 wire contract fixtures; not a firmware or APK build."""
import unittest

MAX_BYTES = 180

def encode(kind, request_id, payload):
    if not (1 <= request_id <= 0xffffffff):
        raise ValueError("request ID")
    if not (1 <= len(kind) <= 16 and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ_" for c in kind)):
        raise ValueError("type")
    if any(c == "|" or ord(c) < 32 or ord(c) == 127 for c in payload):
        raise ValueError("payload")
    frame = f"AI1|{kind}|{request_id}|{payload}\\n".replace("\\\\n", "\\n")
    data = frame.encode("utf-8", errors="strict")
    if len(data) > MAX_BYTES:
        raise ValueError("too large")
    return data

class ContractTests(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(encode("HELLO", 1, "flipper-v1"), b"AI1|HELLO|1|flipper-v1\\n".replace(b"\\\\n", b"\\n"))
    def test_unicode(self):
        self.assertIn("🔊".encode("utf-8"), encode("ASK", 2, "radio 🔊"))
    def test_invalid_id(self):
        for value in (-1, 0, 0x100000000):
            with self.assertRaises(ValueError):
                encode("ASK", value, "battery")
    def test_separator(self):
        with self.assertRaises(ValueError):
            encode("ASK", 1, "a|b")
    def test_size(self):
        with self.assertRaises(ValueError):
            encode("ASK", 1, "x" * 180)
    def test_invalid_surrogate(self):
        with self.assertRaises(UnicodeEncodeError):
            encode("ASK", 1, "\\ud800")

if __name__ == "__main__":
    unittest.main()
