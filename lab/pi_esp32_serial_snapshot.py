"""Offline, read-only ESP32 serial snapshot classifier. Never opens ports or executes commands."""
import json
import re
import sys
import unittest

PORT = re.compile(r'^/dev/(ttyUSB[0-9]+|ttyACM[0-9]+)$')
HEX = re.compile(r'^[0-9a-fA-F]{4}$')


def classify(snapshot):
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get('devices'), list):
        return {'status': 'REJECT', 'reason': 'invalid snapshot'}
    devices = snapshot['devices']
    if len(devices) > 32:
        return {'status': 'REJECT', 'reason': 'too many devices'}
    seen = set()
    result = []
    for device in devices:
        if not isinstance(device, dict):
            return {'status': 'REJECT', 'reason': 'invalid device'}
        port, vid, pid = (device.get(k) for k in ('port', 'vid', 'pid'))
        if not isinstance(port, str) or not PORT.fullmatch(port):
            return {'status': 'REJECT', 'reason': 'invalid port'}
        if port in seen:
            return {'status': 'REJECT', 'reason': 'duplicate port'}
        seen.add(port)
        if not isinstance(vid, str) or not HEX.fullmatch(vid) or not isinstance(pid, str) or not HEX.fullmatch(pid):
            return {'status': 'REJECT', 'reason': 'invalid USB ID'}
        result.append({'port': port, 'usb_id': f'{vid.lower()}:{pid.lower()}', 'identity': 'UNVERIFIED'})
    return {'status': 'OBSERVATION_ONLY', 'devices': result, 'flash_authorized': False}


class OfflineTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(classify({'devices': [{'port': '/dev/ttyUSB0', 'vid': '10C4', 'pid': 'EA60'}]})['status'], 'OBSERVATION_ONLY')
    def test_no_devices(self):
        self.assertEqual(classify({'devices': []})['devices'], [])
    def test_bad_port(self):
        self.assertEqual(classify({'devices': [{'port': '/dev/serial/by-id/x', 'vid': '10c4', 'pid': 'ea60'}]})['status'], 'REJECT')
    def test_duplicate(self):
        d = {'port': '/dev/ttyUSB0', 'vid': '10c4', 'pid': 'ea60'}
        self.assertEqual(classify({'devices': [d, d]})['reason'], 'duplicate port')
    def test_bad_id(self):
        self.assertEqual(classify({'devices': [{'port': '/dev/ttyUSB0', 'vid': 'xyz', 'pid': 'ea60'}]})['status'], 'REJECT')
    def test_non_dict(self):
        self.assertEqual(classify({'devices': [None]})['status'], 'REJECT')
    def test_limit(self):
        self.assertEqual(classify({'devices': [{}] * 33})['reason'], 'too many devices')
    def test_no_flash(self):
        self.assertFalse(classify({'devices': []})['flash_authorized'])


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        try:
            data = json.load(sys.stdin)
            print(json.dumps(classify(data), sort_keys=True))
        except (ValueError, UnicodeError):
            print(json.dumps({'status': 'REJECT', 'reason': 'invalid JSON'}))
            sys.exit(2)
