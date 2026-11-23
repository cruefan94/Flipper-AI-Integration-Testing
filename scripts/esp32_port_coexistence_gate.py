"""Offline ESP32-WROOM / ESP32-S2 serial coexistence safety preflight.

Consumes operator-provided observations only. Never probes ports, resets boards,
opens serial devices, or authorizes programming. Synthetic public fixtures only.
"""
import re

PORT = re.compile(r"(?:/dev/tty(?:USB|ACM)[0-9]+|COM[1-9][0-9]*)\Z", re.I)
CHIPS = frozenset(("esp32-wroom-32", "esp32-s2"))

def inspect_port_plan(devices):
    errors = []
    if not isinstance(devices, list) or not (1 <= len(devices) <= 16):
        return {"valid": False, "flash_authorized": False, "errors": ["device_list"]}
    seen_ports, seen_ids = set(), set()
    for idx, device in enumerate(devices):
        prefix = f"device_{idx}"
        if not isinstance(device, dict):
            errors.append(prefix + "_record")
            continue
        if set(device) != {"label", "claimed_chip", "port", "identity_verified"}:
            errors.append(prefix + "_fields")
            continue
        label, chip, port, verified = (device[k] for k in ("label", "claimed_chip", "port", "identity_verified"))
        if not isinstance(label, str) or not (1 <= len(label) <= 48) or not label.isascii() or not all(c.isalnum() or c in "-_ " for c in label):
            errors.append(prefix + "_label")
        else:
            key = label.strip().casefold()
            if key in seen_ids:
                errors.append(prefix + "_duplicate_label")
            seen_ids.add(key)
        if chip not in CHIPS if isinstance(chip, str) else True:
            errors.append(prefix + "_chip")
        if type(verified) is not bool or not verified:
            errors.append(prefix + "_identity_unverified")
        if not isinstance(port, str) or not PORT.fullmatch(port):
            errors.append(prefix + "_port")
        else:
            key = port.casefold()
            if key in seen_ports:
                errors.append(prefix + "_duplicate_port")
            seen_ports.add(key)
    return {"valid": not errors, "flash_authorized": False, "errors": errors}
