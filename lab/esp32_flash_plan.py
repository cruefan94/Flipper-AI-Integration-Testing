"""Offline, read-only ESP32 command preview. Never opens a port."""
import argparse
import json
import re

CHIPS = {'esp32': 'ESP32-WROOM (classic)', 'esp32s2': 'ESP32-S2'}
PORT = re.compile(r'^/dev/(ttyUSB[0-9]+|ttyACM[0-9]+|serial/by-id/[A-Za-z0-9_.:+-]+)$')

def plan(chip, port, baud=115200):
    if chip not in CHIPS:
        raise ValueError('Unsupported chip: explicit ESP32 or ESP32-S2 selection required')
    if not isinstance(port, str) or not PORT.fullmatch(port) or '..' in port:
        raise ValueError('Invalid Linux serial-device path')
    if baud not in (9600, 57600, 115200, 230400, 460800, 921600):
        raise ValueError('Unsupported baud rate')
    return {'chip': chip, 'board_family': CHIPS[chip], 'port': port,
            'baud': baud, 'preview_argv': ['python3', '-m', 'esptool', '--chip', chip,
                                         '--port', port, '--baud', str(baud), 'chip_id'],
            'executed': False,
            'warning': 'Preview only. No serial access, reset, bootloader change or flashing.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chip', required=True, choices=sorted(CHIPS))
    parser.add_argument('--port', required=True)
    parser.add_argument('--baud', type=int, default=115200)
    args = parser.parse_args()
    try:
        print(json.dumps(plan(args.chip, args.port, args.baud), indent=2))
    except ValueError as exc:
        parser.error(str(exc))

if __name__ == '__main__':
    main()
