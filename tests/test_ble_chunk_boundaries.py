"""BLE notification fragmentation/coalescing simulation for the AI1 contract.

Tests the framing layer only; no hardware or Android runtime is implied.
"""
import unittest
from test_ai1_wire_vectors import encode, decode

MAX_FRAME = 180

class LineReassembler:
    def __init__(self):
        self.pending = bytearray()

    def feed(self, chunk):
        if not isinstance(chunk, bytes):
            raise TypeError("BLE chunk must be bytes")
        self.pending.extend(chunk)
        frames = []
        while True:
            end = self.pending.find(b"\n")
            if end < 0:
                if len(self.pending) > MAX_FRAME:
                    self.pending.clear()
                    raise ValueError("unterminated frame exceeds maximum")
                return frames
            frame = bytes(self.pending[:end + 1])
            del self.pending[:end + 1]
            if len(frame) > MAX_FRAME:
                self.pending.clear()
                raise ValueError("frame exceeds maximum")
            frames.append(decode(frame))

class BleChunkBoundaryTests(unittest.TestCase):
    def test_every_two_way_split(self):
        frame = encode("ANSWER", 42, "UTF-8 café")
        for i in range(len(frame) + 1):
            with self.subTest(split=i):
                reader = LineReassembler()
                self.assertEqual(reader.feed(frame[:i]) + reader.feed(frame[i:]), [("ANSWER", 42, "UTF-8 café")])

    def test_one_byte_chunks(self):
        frame = encode("ASK", 11, "hello")
        reader = LineReassembler()
        out = []
        for byte in frame:
            out.extend(reader.feed(bytes([byte])))
        self.assertEqual(out, [("ASK", 11, "hello")])

    def test_multiple_frames_in_single_notification(self):
        reader = LineReassembler()
        combined = encode("PING", 1, "") + encode("STATUS", 2, "ready")
        self.assertEqual(reader.feed(combined), [("PING", 1, ""), ("STATUS", 2, "ready")])

    def test_reject_oversized_unterminated_stream(self):
        reader = LineReassembler()
        with self.assertRaises(ValueError):
            reader.feed(b"x" * 181)
        self.assertEqual(reader.feed(encode("PING", 1, "")), [("PING", 1, "")])

    def test_reject_oversized_completed_frame(self):
        reader = LineReassembler()
        with self.assertRaises(ValueError):
            reader.feed(b"x" * 181 + b"\n")

    def test_utf8_split_inside_multibyte_character(self):
        frame = encode("ANSWER", 3, "café")
        i = frame.index(b"\xc3") + 1
        reader = LineReassembler()
        self.assertEqual(reader.feed(frame[:i]), [])
        self.assertEqual(reader.feed(frame[i:]), [("ANSWER", 3, "café")])

if __name__ == "__main__":
    unittest.main()
