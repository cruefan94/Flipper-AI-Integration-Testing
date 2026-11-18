"""Read-only, bounded Pi USB/desktop crash triage. No privilege or hardware writes."""
import json
import re
import subprocess
import tempfile

CHECKS = {
    'power': ['vcgencmd', 'get_throttled'],
    'memory': ['free', '-h'],
    'storage': ['df', '-h', '/'],
    'previous_boot_warnings': ['journalctl', '-b', '-1', '-p', 'warning', '--no-pager', '-n', '40'],
    'current_boot_warnings': ['journalctl', '-b', '0', '-p', 'warning', '--no-pager', '-n', '40'],
    'current_kernel_usb': ['journalctl', '-b', '0', '-k', '--no-pager', '-n', '100'],
    'previous_kernel_usb': ['journalctl', '-b', '-1', '-k', '--no-pager', '-n', '100'],
    'usb_devices': ['lsusb'],
}
PATTERNS = {
    'undervoltage': r'under.?voltage|voltage.*low',
    'out_of_memory': r'out.of.memory|oom.killer|killed process',
    'usb_reset': r'usb.*(disconnect|reset|error -71|error -110)',
    'desktop_failure': r'labwc|wayfire|segfault|drm.*error',
    'storage_error': r'mmc.*(error|timeout)|i/o error',
}

def bounded_run(argv, **kwargs):
    """Spool bounded journal command output to disk, not an unbounded RAM pipe."""
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        p = subprocess.run(argv, stdout=out, stderr=err,
                           timeout=kwargs.get('timeout', 8), check=False)
        out.seek(max(0, out.tell() - 6000))
        err.seek(max(0, err.tell() - 400))
        return subprocess.CompletedProcess(argv, p.returncode,
            out.read().decode('utf-8', errors='replace'),
            err.read().decode('utf-8', errors='replace'))

def collect(runner=None):
    runner = runner or bounded_run
    result = {}
    for name, argv in CHECKS.items():
        try:
            p = runner(argv, capture_output=True, text=True, timeout=8, check=False)
            result[name] = {'exit_code': p.returncode, 'output': p.stdout[-6000:],
                            'error': p.stderr[-400:]}
        except (OSError, subprocess.TimeoutExpired) as exc:
            result[name] = {'error': type(exc).__name__}
    return result

def analyze(snapshot):
    text = '\n'.join(str(x.get('output', '')) for x in snapshot.values())
    matches = {name: bool(re.search(pattern, text, re.I)) for name, pattern in PATTERNS.items()}
    power = snapshot.get('power', {}).get('output', '')
    flag = re.search(r'throttled=0x([0-9a-fA-F]+)', power)
    if flag:
        value = int(flag.group(1), 16)
        matches['current_undervoltage_flag'] = bool(value & 1)
        matches['historical_undervoltage_flag'] = bool(value & (1 << 16))
    return matches

def main():
    snapshot = collect()
    print(json.dumps({'checks': snapshot, 'signals_not_diagnoses': analyze(snapshot)}, indent=2))

if __name__ == '__main__':
    main()
