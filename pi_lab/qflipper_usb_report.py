"""Privacy-minimal, offline USB inventory report for the Pi qFlipper workstation.

Consumes already parsed owner-provided lsusb evidence. Does not identify a
Flipper, run commands, connect devices, back up data, or authorize flashing.
"""
from dataclasses import dataclass
from .qflipper_usb_evidence import UsbDevice


@dataclass(frozen=True)
class UsbSummary:
    device_count: int
    unique_vid_pid_count: int
    entries: tuple[str, ...]
    conclusion: str = "USB enumeration only; qFlipper connection unverified"


def summarize_usb(devices: tuple[UsbDevice, ...]) -> UsbSummary:
    if not isinstance(devices, tuple) or len(devices) > 256:
        raise ValueError("expected bounded tuple of USB devices")
    seen = set()
    ids = set()
    entries = []
    for item in devices:
        if not isinstance(item, UsbDevice):
            raise ValueError("invalid USB evidence")
        if (not (item.bus.isascii() and len(item.bus) == 3 and item.bus.isdigit())
                or not (item.device.isascii() and len(item.device) == 3 and item.device.isdigit())
                or not all(len(x) == 4 and x.isascii() and all(c in "0123456789abcdef" for c in x)
                           for x in (item.vid, item.pid))):
            raise ValueError("invalid USB evidence fields")
        location = (item.bus, item.device)
        if location in seen:
            raise ValueError("duplicate USB location")
        seen.add(location)
        ids.add((item.vid, item.pid))
        entries.append(f"Bus {item.bus} Device {item.device}: {item.vid}:{item.pid}")
    return UsbSummary(len(entries), len(ids), tuple(sorted(entries)))
