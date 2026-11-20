"""Offline ESP32 serial inventory classifier; no device access or flashing."""
import json
import re
import sys

PORT = re.compile(r'^/dev/(ttyUSB|ttyACM)[0-9]+$')
HEX = re.compile(r'^[0-9a-fA-F]{4}$')

def inspect_inventory(data):
    if not isinstance(data, dict) or set(data) != {'ports', 'usb_devices'}:
        return {'ready': False, 'errors': ['invalid inventory schema'], 'candidates': []}
    ports, devices = data['ports'], data['usb_devices']
    if not isinstance(ports, list) or not isinstance(devices, list) or len(ports) > 64 or len(devices) > 64:
        return {'ready': False, 'errors': ['invalid inventory lists'], 'candidates': []}
    errors, candidates, seen = [], [], set()
    for p in ports:
        if not isinstance(p, dict) or set(p) != {'path', 'vid', 'pid'}:
            errors.append('invalid port record'); continue
        path, vid, pid = p['path'], p['vid'], p['pid']
        if not isinstance(path, str) or not PORT.fullmatch(path) or not isinstance(vid, str) or not HEX.fullmatch(vid) or not isinstance(pid, str) or not HEX.fullmatch(pid):
            errors.append('invalid port identity'); continue
        if path in seen:
            errors.append('duplicate serial port'); continue
        seen.add(path)
        candidates.append({'path': path, 'usb_id': f'{vid.lower()}:{pid.lower()}', 'status': 'unverified - manual board identification required'})
    for d in devices:
        if not isinstance(d, dict) or set(d) != {'vid', 'pid'} or not all(isinstance(d[k], str) and HEX.fullmatch(d[k]) for k in ('vid', 'pid')):
            errors.append('invalid USB record')
    if not candidates:
        errors.append('no serial candidates')
    return {'ready': False, 'errors': errors, 'candidates': candidates}

def main():
    try:
        result = inspect_inventory(json.load(sys.stdin))
    except (ValueError, UnicodeError):
        result = {'ready': False, 'errors': ['invalid JSON'], 'candidates': []}
    print(json.dumps(result, sort_keys=True))
    return 0 if not result['errors'] else 2

if __name__ == '__main__':
    sys.exit(main())
