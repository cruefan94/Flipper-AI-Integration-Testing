"""Offline-only Pi USB observation validation. Never opens serial devices."""
import json
import re
import sys

PORT = re.compile(r'^/dev/tty(?:USB|ACM)(?:0|[1-9][0-9]*)$')
HEX4 = re.compile(r'^[0-9a-fA-F]{4}$')

def validate(snapshot):
    if not isinstance(snapshot, dict) or set(snapshot) != {'observations'}:
        raise ValueError('expected observations only')
    rows = snapshot['observations']
    if not isinstance(rows, list) or len(rows) > 16:
        raise ValueError('expected at most 16 observations')
    seen = set()
    out = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'port', 'vid', 'pid', 'operator_label'}:
            raise ValueError('invalid observation fields')
        port, vid, pid, label = (row[k] for k in ('port', 'vid', 'pid', 'operator_label'))
        if not isinstance(port, str) or not PORT.fullmatch(port):
            raise ValueError('noncanonical Linux serial port')
        if not isinstance(vid, str) or not HEX4.fullmatch(vid) or not isinstance(pid, str) or not HEX4.fullmatch(pid):
            raise ValueError('VID/PID must be four hex digits')
        if not isinstance(label, str) or not 1 <= len(label) <= 40 or not label.isprintable() or not label.strip():
            raise ValueError('invalid operator label')
        if port in seen:
            raise ValueError('duplicate port')
        seen.add(port)
        out.append({'port': port, 'usb_id': f'{vid.lower()}:{pid.lower()}', 'operator_label': label.strip(), 'identity_verified': False, 'flash_authorized': False})
    return {'observations': out, 'flash_authorized': False, 'warning': 'Operator-supplied observations only; USB IDs do not prove chip identity or authorization.'}

def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 pi_usb_snapshot.py observations.json')
    with open(sys.argv[1], 'rb') as f:
        raw = f.read(32769)
    if len(raw) > 32768:
        raise SystemExit('Input exceeds 32 KiB')
    try:
        print(json.dumps(validate(json.loads(raw)), indent=2))
    except (ValueError, UnicodeError) as exc:
        raise SystemExit(f'REJECTED: {exc}') from exc

if __name__ == '__main__':
    main()
