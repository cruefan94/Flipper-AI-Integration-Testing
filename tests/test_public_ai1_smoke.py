"""Public-safe AI1 framing smoke tests; illustrative contract, not production parity."""
import unittest

MAX_FRAME = 256

def parse_frame(raw):
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_FRAME or not raw.endswith(b'\n'):
        raise ValueError('invalid frame')
    if b'\r' in raw or b'\x00' in raw:
        raise ValueError('invalid control byte')
    try:
        text = raw[:-1].decode('utf-8', errors='strict')
    except UnicodeDecodeError as exc:
        raise ValueError('invalid utf8') from exc
    parts = text.split('|', 2)
    if len(parts) != 3 or parts[0] not in ('HELLO', 'ASK', 'ANSWER', 'ERROR'):
        raise ValueError('invalid message type')
    if not parts[1].isascii() or not parts[1].isdigit() or len(parts[1]) > 10:
        raise ValueError('invalid request id')
    request_id = int(parts[1])
    if request_id == 0 or request_id > 0xffffffff:
        raise ValueError('invalid request id')
    if not parts[2]:
        raise ValueError('empty payload')
    return parts[0], request_id, parts[2]

class PublicContractTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(parse_frame(b'ASK|7|hello\n'), ('ASK', 7, 'hello'))
    def test_invalid(self):
        for raw in [b'', b'ASK|1|hello', b'ASK|0|hello\n', b'ASK|4294967296|x\n', b'ASK|1|\n', b'ASK|1|x\x00\n', b'ASK|1|x\r\n', b'ASK|1|\xff\n', b'ASK|1|'+b'x'*260+b'\n', b'OTHER|1|x\n', b'ASK|+1|x\n']:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    parse_frame(raw)

if __name__ == '__main__':
    unittest.main()
