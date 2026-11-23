#!/usr/bin/env python3
"""Offline, public-safe ESP32 boot trace classifier. Never opens serial devices."""
import json
import re
import sys

BOOT_MODES = {'download', 'normal', 'unknown'}
HEX = re.compile(r'^[0-9a-fA-F]{4}:[0-9a-fA-F]{4}$')

def classify(record):
    if not isinstance(record, dict):
        raise ValueError('record must be an object')
    required = {'board_label', 'usb_vid_pid', 'boot_held_low', 'en_reset_observed', 'reported_mode'}
    if set(record) != required:
        raise ValueError('required fields must match exactly')
    if not isinstance(record['board_label'], str) or not 1 <= len(record['board_label'].strip()) <= 80:
        raise ValueError('invalid board label')
    if not isinstance(record['usb_vid_pid'], str) or not HEX.fullmatch(record['usb_vid_pid']):
        raise ValueError('invalid USB VID:PID')
    if type(record['boot_held_low']) is not bool or type(record['en_reset_observed']) is not bool:
        raise ValueError('switch observations must be booleans')
    if record['reported_mode'] not in BOOT_MODES:
        raise ValueError('invalid mode')
    if record['reported_mode'] == 'download' and record['boot_held_low'] and record['en_reset_observed']:
        status = 'consistent_download_observation'
    elif record['reported_mode'] == 'download':
        status = 'inconsistent_download_observation'
    else:
        status = 'insufficient_download_evidence'
    return {'status': status, 'board_identity_verified': False, 'flash_authorized': False,
            'next_step': 'Confirm exact board schematic and manually inspect read-only boot log'}

def main():
    if len(sys.argv) != 2 or sys.argv[1] != '--stdin-json':
        print('Usage: esp32_boot_trace_gate.py --stdin-json', file=sys.stderr)
        return 2
    try:
        data = json.load(sys.stdin)
        print(json.dumps(classify(data), sort_keys=True))
        return 0
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        print('REJECTED: ' + str(e), file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
