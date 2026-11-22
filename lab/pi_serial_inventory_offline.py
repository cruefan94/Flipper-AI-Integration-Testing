#!/usr/bin/env python3
"""Offline parser for owner-pasted Raspberry Pi serial device listings.

Never opens a device, toggles GPIO, resets or flashes a board.
Usage: python3 pi_serial_inventory_offline.py --self-test
       python3 pi_serial_inventory_offline.py < saved_ls_output.txt
Input: output of 'ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null'
No serial data, secrets or device identifiers are uploaded.
"""
import re
import sys

DEVICE = re.compile(r"(?<![\w/])(/dev/tty(?:USB|ACM)[0-9]+)(?![\w/])")
def inventory(text):
    return sorted(set(DEVICE.findall(text)))

def render(text):
    found = inventory(text)
    if not found:
        return "No ttyUSB/ttyACM paths found in supplied text. Check USB cable, power and lsusb locally."
    return "\n".join(f"Possible serial port: {p} (NOT verified as ESP32)" for p in found)

def self_test():
    cases = [
        ("crw-rw---- 1 root dialout 188, 0 Nov 22 04:00 /dev/ttyUSB0", ["/dev/ttyUSB0"]),
        ("/dev/ttyACM1 /dev/ttyUSB2 /dev/ttyACM1", ["/dev/ttyACM1", "/dev/ttyUSB2"]),
        ("/dev/ttyUSB0evil /tmp/ttyUSB0 /dev/ttyS0", []),
        ("ls: cannot access '/dev/ttyUSB*': No such file", []),
        ("", []),
    ]
    for source, expected in cases:
        assert inventory(source) == expected, (source, inventory(source), expected)
    print(f"PASS: {len(cases)} offline serial inventory cases")

if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
    elif len(sys.argv) == 1:
        print(render(sys.stdin.read()))
    else:
        sys.exit("Usage: --self-test or pipe saved ls output on stdin")
