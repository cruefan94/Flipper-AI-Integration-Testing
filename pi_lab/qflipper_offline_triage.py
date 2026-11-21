"""Offline, redacted qFlipper diagnostic categorizer. Never opens USB or logs."""
import re
import unittest

RULES = (
    ("dfu_crc", re.compile(r"\\b(?:dfu.{0,40}crc|crc.{0,40}dfu|crc.{0,15}9-99)\\b", re.I)),
    ("usb_permission", re.compile(r"permission denied|access denied|libusb.*(?:denied|access)", re.I)),
    ("usb_missing", re.compile(r"no (?:flipper|device) found|device not found|no such device", re.I)),
    ("serial_busy", re.compile(r"resource busy|device or resource busy|port.*in use", re.I)),
    ("transfer_timeout", re.compile(r"timed out|timeout|transfer.*failed", re.I)),
)
ADVICE = {
    "dfu_crc": "Quarantine this updater; do not retry the failed F7 image.",
    "usb_permission": "Check local udev permissions without privileged automation.",
    "usb_missing": "Inspect cable, USB enumeration and device state manually.",
    "serial_busy": "Close competing serial/qFlipper sessions before retrying diagnostics.",
    "transfer_timeout": "Inspect USB cable and power; do not assume firmware corruption.",
    "unclassified": "Review locally with sensitive fields redacted; no flash recommended.",
}

def classify(log_text):
    """Return fixed labels only, never echo user-provided logs or identifiers."""
    if not isinstance(log_text, str):
        raise TypeError("log_text must be text")
    hits = [name for name, pattern in RULES if pattern.search(log_text[:200000])]
    return [{"code": name, "guidance": ADVICE[name]} for name in hits] or [
        {"code": "unclassified", "guidance": ADVICE["unclassified"]}
    ]

class OfflineTests(unittest.TestCase):
    def test_crc(self):
        self.assertEqual(classify("DFU CRC error 9-99")[0]["code"], "dfu_crc")
    def test_permission(self):
        self.assertEqual(classify("libusb access denied")[0]["code"], "usb_permission")
    def test_missing(self):
        self.assertEqual(classify("No Flipper found")[0]["code"], "usb_missing")
    def test_busy(self):
        self.assertEqual(classify("device or resource busy")[0]["code"], "serial_busy")
    def test_timeout(self):
        self.assertEqual(classify("transfer timed out")[0]["code"], "transfer_timeout")
    def test_no_echo_of_secret(self):
        result = str(classify("token=PRIVATE-DO-NOT-PRINT"))
        self.assertNotIn("PRIVATE", result)
    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            classify(None)
    def test_no_hardware_access(self):
        self.assertEqual(classify("ordinary status")[0]["code"], "unclassified")

if __name__ == "__main__":
    unittest.main()
