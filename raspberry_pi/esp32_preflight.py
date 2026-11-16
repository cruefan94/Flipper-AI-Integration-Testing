#!/usr/bin/env python3
"""Read-only ESP32 serial flashing preflight for Raspberry Pi 4B.

NEVER opens a serial port, changes GPIO/BOOT/EN, or flashes a board.
"""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import stat


def classify_port(name):
    """Advisory category, not verified board identity."""
    if name.startswith('/dev/ttyUSB'):
        return 'USB-UART bridge (possible ESP32-WROOM)'
    if name.startswith('/dev/ttyACM'):
        return 'USB CDC serial (board identity unverified)'
    if name.startswith('/dev/serial/by-id/'):
        return 'persistent USB serial symlink (preferred when present)'
    if name.startswith('/dev/ttyAMA') or name.startswith('/dev/ttyS'):
        return 'Pi onboard UART: check console, voltage and pinout before use'
    return 'unrecognized path: do not assume ESP32 compatibility'


def inspect_port(name):
    path = Path(name)
    result = {'port': name, 'category': classify_port(name),
              'exists': path.exists(), 'character_device': False,
              'read_write_access': False, 'safe_to_flash': False}
    if path.exists():
        result['character_device'] = stat.S_ISCHR(path.stat().st_mode)
        result['read_write_access'] = os.access(path, os.R_OK | os.W_OK)
    return result


def report(ports):
    try:
        version = importlib.metadata.version('esptool')
    except importlib.metadata.PackageNotFoundError:
        version = None
    return {'mode': 'read_only_preflight', 'esptool_version': version,
            'ports': [inspect_port(p) for p in ports],
            'notes': [
                'Port detection does not prove an ESP32 is attached.',
                'ESP32-WROOM ROM download mode: hold GPIO0/BOOT LOW while resetting EN, then release BOOT.',
                'Common ground and 3.3 V UART logic are mandatory; never feed 5 V into ESP32 GPIO.',
                'For Pi USB flashing, prefer a known-good data cable and dedicated ESP32 USB-UART adapter.',
                'Do not wire the official ESP32-S2 Flipper devboard and WROOM UART outputs together.',
                'No flashing, serial probing, GPIO toggling or remote hardware control was performed.'
            ]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', action='append', default=[], help='Serial device to inspect without opening it')
    args = parser.parse_args()
    ports = args.port or sorted([str(p) for pattern in ('ttyUSB*', 'ttyACM*')
                                 for p in Path('/dev').glob(pattern)])
    print(json.dumps(report(ports), indent=2))


if __name__ == '__main__':
    main()
