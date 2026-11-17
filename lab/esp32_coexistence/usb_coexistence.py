"""Offline USB snapshot coexistence review; no hardware access."""
from collections import Counter

SUPPORTED = {'esp32-wroom', 'esp32-s2', 'flipper-zero', 'arduino-uno'}

def review(devices):
    """Return fail-closed observations, never permission to flash."""
    errors = []
    if not isinstance(devices, list) or not devices:
        return {'ok': False, 'errors': ['missing_snapshot'], 'flash_authorized': False}
    ports, identities = [], []
    for i, d in enumerate(devices):
        if not isinstance(d, dict):
            errors.append(f'{i}:invalid_record'); continue
        kind, port, serial = (d.get(k) for k in ('board', 'port', 'serial'))
        if kind not in SUPPORTED: errors.append(f'{i}:unsupported_board')
        if not isinstance(port, str) or not port.startswith('/dev/serial/by-id/') or port.endswith('/'):
            errors.append(f'{i}:unstable_port')
        else: ports.append(port)
        if not isinstance(serial, str) or not serial.strip() or serial.lower() in {'unknown','none','null'}:
            errors.append(f'{i}:missing_serial')
        else: identities.append((kind, serial))
    if any(n > 1 for n in Counter(ports).values()): errors.append('duplicate_port')
    if any(n > 1 for n in Counter(identities).values()): errors.append('duplicate_identity')
    return {'ok': not errors, 'errors': errors, 'flash_authorized': False}
