"""Offline public-safe serial-port preflight. Never opens a port or flashes."""
import json
import re
import sys

PORT = re.compile(r'^/dev/(ttyUSB|ttyACM)[0-9]+$')
BOARD_TYPES = {'esp32-wroom', 'esp32-s2', 'flipper-zero', 'arduino-uno'}

def review(snapshot):
    if not isinstance(snapshot, list) or not snapshot:
        return {'status': 'BLOCKED', 'reasons': ['missing_snapshot']}
    reasons = []
    ports, identities = set(), set()
    for index, item in enumerate(snapshot):
        if not isinstance(item, dict):
            reasons.append(f'{index}:invalid_record')
            continue
        port, board, serial = (item.get(k) for k in ('port', 'board', 'serial'))
        if not isinstance(port, str) or not PORT.fullmatch(port):
            reasons.append(f'{index}:invalid_port')
        elif port in ports:
            reasons.append(f'{index}:duplicate_port')
        else:
            ports.add(port)
        if board not in BOARD_TYPES:
            reasons.append(f'{index}:unsupported_board')
        if not isinstance(serial, str) or not serial.strip() or serial.strip().lower() in {'unknown', 'none', 'n/a'}:
            reasons.append(f'{index}:unverified_serial')
        elif (board, serial) in identities:
            reasons.append(f'{index}:duplicate_identity')
        else:
            identities.add((board, serial))
    return {'status': 'BLOCKED' if reasons else 'REVIEW_ONLY', 'reasons': reasons}

if __name__ == '__main__':
    print(json.dumps(review(json.load(sys.stdin)), sort_keys=True))
