#!/usr/bin/env python3
"""Offline DFU suffix CRC gate. Run ONLY on locally authorized private artifacts.

No network, no logging of paths, no artifact uploads. This is not a device flash
or a substitute for source provenance, updater manifest and hardware acceptance.
"""
import argparse
import pathlib
import struct
import sys
import unittest
import zlib

SUFFIX_LEN = 16


def verify_dfu(data: bytes) -> tuple[bool, str]:
    if len(data) < SUFFIX_LEN:
        return False, "missing-or-short-suffix"
    suffix = data[-SUFFIX_LEN:]
    if suffix[8:11] != b"UFD" or suffix[11] != SUFFIX_LEN:
        return False, "invalid-dfu-suffix-signature-or-length"
    expected = struct.unpack("<I", suffix[12:16])[0]
    actual = zlib.crc32(data[:-4]) & 0xFFFFFFFF
    if actual != expected:
        return False, "dfu-crc-mismatch"
    return True, "valid-dfu-suffix-crc-only"


class SyntheticTests(unittest.TestCase):
    @staticmethod
    def fixture(payload=b"synthetic-not-firmware"):
        suffix = struct.pack("<HHHH", 0, 0, 0, 0x011A) + b"UFD" + bytes([16])
        prefix = payload + suffix
        return prefix + struct.pack("<I", zlib.crc32(prefix) & 0xFFFFFFFF)

    def test_valid_synthetic(self):
        self.assertTrue(verify_dfu(self.fixture())[0])

    def test_corrupted_payload(self):
        data = bytearray(self.fixture())
        data[0] ^= 1
        self.assertEqual(verify_dfu(data)[1], "dfu-crc-mismatch")

    def test_corrupted_crc(self):
        data = bytearray(self.fixture())
        data[-1] ^= 1
        self.assertEqual(verify_dfu(data)[1], "dfu-crc-mismatch")

    def test_missing_suffix(self):
        self.assertFalse(verify_dfu(b"not-a-dfu")[0])

    def test_bad_signature(self):
        data = bytearray(self.fixture())
        data[-8] = ord("X")
        self.assertFalse(verify_dfu(data)[0])

    def test_wrong_length(self):
        data = bytearray(self.fixture())
        data[-5] = 15
        self.assertFalse(verify_dfu(data)[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dfu", nargs="?", type=pathlib.Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(SyntheticTests)
        return 0 if unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful() else 1
    if args.dfu is None:
        parser.error("provide local firmware.dfu or --self-test")
    try:
        data = args.dfu.read_bytes()
    except OSError:
        print("BLOCKED: unable to read local DFU", file=sys.stderr)
        return 2
    valid, reason = verify_dfu(data)
    print(("PASS" if valid else "FAIL") + ": " + reason)
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
