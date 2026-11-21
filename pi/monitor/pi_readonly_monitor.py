"""Pi-side read-only system snapshot; no GPIO, network, or subprocess calls."""
import argparse
import json
import time
from pathlib import Path


def read_text(path):
    try:
        return Path(path).read_text(encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        return None


def parse_meminfo(raw):
    result = {}
    for line in (raw or '').splitlines():
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        if key in ('MemTotal', 'MemAvailable'):
            try:
                result[key] = int(value.strip().split()[0])
            except (ValueError, IndexError):
                pass
    return result


def snapshot(root='/'):
    root = Path(root)
    def file(name):
        return read_text(root / name.lstrip('/'))
    mem = parse_meminfo(file('/proc/meminfo'))
    temp = file('/sys/class/thermal/thermal_zone0/temp')
    try:
        temp_c = round(int(temp.strip()) / 1000, 1) if temp else None
    except ValueError:
        temp_c = None
    uptime = file('/proc/uptime')
    try:
        uptime_s = int(float(uptime.split()[0])) if uptime else None
    except (ValueError, IndexError):
        uptime_s = None
    return {'temperature_c': temp_c, 'uptime_s': uptime_s,
            'memory_total_kib': mem.get('MemTotal'),
            'memory_available_kib': mem.get('MemAvailable'),
            'pironman_oled': 'not_probed', 'flipper_usb': 'not_probed',
            'esp32': 'not_probed'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--once', action='store_true', help='One read-only snapshot then exit')
    p.add_argument('--interval', type=int, default=10, help='Polling seconds (minimum 10)')
    args = p.parse_args()
    if args.interval < 10:
        p.error('interval must be at least 10 seconds')
    while True:
        print(json.dumps(snapshot(), sort_keys=True), flush=True)
        if args.once:
            return
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
