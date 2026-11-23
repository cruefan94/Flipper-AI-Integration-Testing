"""Offline, read-only parser of owner-supplied lsusb output.

Never invokes commands, opens USB devices, or stores serial numbers.
A matching VID:PID is only USB enumeration evidence, NOT proof of qFlipper
connectivity, RPC functionality, backups, or firmware compatibility.
"""
import re
from dataclasses import dataclass

LINE = re.compile(r"^Bus ([0-9]{3}) Device ([0-9]{3}): ID ([0-9a-fA-F]{4}):([0-9a-fA-F]{4})(?:\s+.*)?$")
MAX_BYTES = 32768
MAX_LINES = 256


@dataclass(frozen=True)
class UsbDevice:
    bus: str
    device: str
    vid: str
    pid: str


def parse_lsusb(snapshot: str) -> tuple[UsbDevice, ...]:
    if not isinstance(snapshot, str):
        raise ValueError("snapshot must be text")
    if len(snapshot.encode("utf-8")) > MAX_BYTES:
        raise ValueError("snapshot too large")
    lines = snapshot.splitlines()
    if len(lines) > MAX_LINES:
        raise ValueError("too many lines")
    devices = []
    seen = set()
    for line in lines:
        if not line.strip():
            continue
        match = LINE.fullmatch(line.strip())
        if not match:
            raise ValueError("invalid lsusb line")
        bus, device, vid, pid = match.groups()
        key = (bus, device)
        if key in seen:
            raise ValueError("duplicate bus/device")
        seen.add(key)
        devices.append(UsbDevice(bus, device, vid.lower(), pid.lower()))
    return tuple(devices)


def matches_vid_pid(devices: tuple[UsbDevice, ...], vid: str, pid: str) -> bool:
    """Caller supplies verified device IDs; no Flipper IDs are assumed."""
    if not all(isinstance(x, str) and re.fullmatch(r"[0-9a-fA-F]{4}", x) for x in (vid, pid)):
        raise ValueError("VID/PID must be four hexadecimal digits")
    return any(d.vid == vid.lower() and d.pid == pid.lower() for d in devices)
