"""Offline Raspberry Pi ESP32 USB identity stability gate. No serial I/O or flashing."""
import json
import re
import sys
import unittest
from copy import deepcopy

PORT = re.compile(r'^/dev/serial/by-id/[A-Za-z0-9_.:+-]+$')
HEX = re.compile(r'^[0-9a-fA-F]{4}$')
CHIPS = {'esp32', 'esp32-s2'}

def assess(data):
    errors = []
    if not isinstance(data, dict):
        return ['observation must be an object']
    observations = data.get('observations')
    if not isinstance(observations, list) or len(observations) < 2:
        return ['at least two independent observations required']
    expected = data.get('expected_chip')
    if expected not in CHIPS:
        errors.append('expected chip must be esp32 or esp32-s2')
    identities = []
    for index, item in enumerate(observations):
        prefix = f'observation {index + 1}'
        if not isinstance(item, dict):
            errors.append(f'{prefix}: invalid object')
            continue
        path, vid, pid, serial, chip = (item.get(k) for k in ('port', 'vid', 'pid', 'serial', 'chip'))
        if not isinstance(path, str) or not PORT.fullmatch(path) or '..' in path:
            errors.append(f'{prefix}: unsafe or unstable port path')
        if not isinstance(vid, str) or not HEX.fullmatch(vid) or not isinstance(pid, str) or not HEX.fullmatch(pid):
            errors.append(f'{prefix}: invalid VID/PID')
        if not isinstance(serial, str) or not re.fullmatch(r'[A-Za-z0-9_.-]{4,80}', serial):
            errors.append(f'{prefix}: missing or invalid serial identity')
        if chip != expected:
            errors.append(f'{prefix}: chip mismatch')
        if all(not e.startswith(prefix) for e in errors):
            identities.append((path, vid.lower(), pid.lower(), serial, chip))
    if len(identities) == len(observations) and len(set(identities)) != 1:
        errors.append('device identity changed between observations')
    return errors

BASE = {'expected_chip': 'esp32', 'observations': [
    {'port': '/dev/serial/by-id/usb-CP2102_1234', 'vid': '10c4', 'pid': 'ea60', 'serial': 'CP2102-1234', 'chip': 'esp32'},
    {'port': '/dev/serial/by-id/usb-CP2102_1234', 'vid': '10C4', 'pid': 'EA60', 'serial': 'CP2102-1234', 'chip': 'esp32'}]}

class OfflineTests(unittest.TestCase):
    def test_stable(self): self.assertEqual(assess(BASE), [])
    def test_s2(self):
        d = deepcopy(BASE); d['expected_chip'] = 'esp32-s2'
        for item in d['observations']: item['chip'] = 'esp32-s2'
        self.assertEqual(assess(d), [])
    def test_changed_serial(self):
        d = deepcopy(BASE); d['observations'][1]['serial'] = 'DIFFERENT'
        self.assertTrue(assess(d))
    def test_changed_port(self):
        d = deepcopy(BASE); d['observations'][1]['port'] = '/dev/serial/by-id/usb-other'
        self.assertTrue(assess(d))
    def test_unstable_tty(self):
        d = deepcopy(BASE); d['observations'][0]['port'] = '/dev/ttyUSB0'
        self.assertTrue(assess(d))
    def test_traversal(self):
        d = deepcopy(BASE); d['observations'][0]['port'] = '/dev/serial/by-id/..'
        self.assertTrue(assess(d))
    def test_bad_vid(self):
        d = deepcopy(BASE); d['observations'][0]['vid'] = 'zzzz'
        self.assertTrue(assess(d))
    def test_chip_mismatch(self):
        d = deepcopy(BASE); d['observations'][1]['chip'] = 'esp32-s2'
        self.assertTrue(assess(d))
    def test_single_observation(self):
        d = deepcopy(BASE); d['observations'] = d['observations'][:1]
        self.assertTrue(assess(d))
    def test_invalid_item(self):
        d = deepcopy(BASE); d['observations'][0] = None
        self.assertTrue(assess(d))
    def test_missing_serial(self):
        d = deepcopy(BASE); d['observations'][0]['serial'] = ''
        self.assertTrue(assess(d))
    def test_nonobject(self): self.assertTrue(assess([]))

def main():
    if len(sys.argv) == 2 and sys.argv[1] == '--self-test':
        unittest.main(argv=[sys.argv[0]], exit=False)
        return
    if len(sys.argv) != 2:
        raise SystemExit('usage: python pi_usb_identity_stability.py observations.json | --self-test')
    try:
        with open(sys.argv[1], encoding='utf-8') as file:
            data = json.load(file)
        errors = assess(data)
    except (OSError, ValueError) as exc:
        raise SystemExit(f'BLOCKED: invalid input: {exc}')
    print('BLOCKED: ' + '; '.join(errors) if errors else 'PASS: offline identity consistent; NOT authorization to flash')
    raise SystemExit(1 if errors else 0)

if __name__ == '__main__':
    main()
