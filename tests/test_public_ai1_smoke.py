"""Public independent AI1 fixture, aligned to Android SatelliteProtocol grammar."""
import unittest

MAX_FRAME = 180

def parse_frame(raw):
    if not isinstance(raw, bytes) or not 11 <= len(raw) <= MAX_FRAME or not raw.endswith(b'\n'):
        raise ValueError("frame")
    try:
        value = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("utf8") from exc
    fields = value[:-1].split("|")
    if len(fields) != 4 or fields[0] != "AI1":
        raise ValueError("version or field count")
    typ, id_text, payload = fields[1:]
    if not 1 <= len(typ) <= 16 or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ_" for c in typ):
        raise ValueError("type")
    if not 1 <= len(id_text) <= 10 or any(c not in "0123456789" for c in id_text):
        raise ValueError("id")
    request_id = int(id_text)
    if not 1 <= request_id <= 4294967295:
        raise ValueError("id range")
    if any(ord(c) < 32 or ord(c) == 127 for c in payload):
        raise ValueError("payload control")
    return typ, request_id, payload

class PublicContractTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(parse_frame(b"AI1|ASK|7|hello\n"), ("ASK", 7, "hello"))
        self.assertEqual(parse_frame("AI1|ANSWER|4294967295|café\n".encode())[1], 4294967295)

    def test_invalid(self):
        bad = [b"", b"ASK|1|hello\n", b"AI1|ASK|1|hello", b"AI1|ASK|0|x\n",
               b"AI1|ASK|4294967296|x\n", b"AI1|ASK|+1|x\n", b"AI1|ASK|1|x|y\n",
               b"AI1|ASK|1|x\r\n", b"AI1|ASK|1|x\x00\n", b"AI1|ASK|1|\xff\n",
               b"AI1|ASK|1|" + b"x"*180 + b"\n", "AI1|ASK|１２|x\n".encode()]
        for frame in bad:
            with self.subTest(frame=frame), self.assertRaises(ValueError):
                parse_frame(frame)

if __name__ == "__main__":
    unittest.main()
