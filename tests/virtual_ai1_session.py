"""Host-only AI1 virtual session; no claim of MCU/BLE hardware emulation."""
from dataclasses import dataclass
from typing import Optional

from test_ai1_contract import encode

@dataclass
class VirtualAi1Session:
    connected: bool = False
    trusted: bool = False
    pending: Optional[int] = None
    generation: int = 0

    def connect(self, trusted: bool):
        self.generation += 1
        self.connected = True
        self.trusted = trusted
        self.pending = None

    def disconnect(self):
        self.generation += 1
        self.connected = False
        self.trusted = False
        self.pending = None

    def request(self, request_id: int, payload: str) -> bytes:
        if not self.connected or not self.trusted:
            raise PermissionError("untrusted or disconnected")
        if self.pending is not None:
            raise RuntimeError("request already pending")
        frame = encode("ASK", request_id, payload)
        self.pending = request_id
        return frame

    def response(self, frame: bytes, generation: int) -> str:
        if not self.connected or not self.trusted or generation != self.generation:
            raise PermissionError("stale or untrusted session")
        if len(frame) > 180 or not frame.endswith(b"\n"):
            raise ValueError("frame boundary")
        try:
            raw = frame[:-1].decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise ValueError("invalid utf8") from exc
        parts = raw.split("|")
        if len(parts) != 4 or parts[0] != "AI1" or parts[1] != "ANSWER":
            raise ValueError("invalid response")
        try:
            rid = int(parts[2])
        except ValueError as exc:
            raise ValueError("invalid id") from exc
        if not parts[2].isdigit() or not (1 <= rid <= 0xffffffff):
            raise ValueError("invalid id")
        if rid != self.pending:
            raise ValueError("unexpected or replayed id")
        payload = parts[3]
        if any(ord(c) < 32 or ord(c) == 127 for c in payload):
            raise ValueError("control in payload")
        self.pending = None
        return payload
