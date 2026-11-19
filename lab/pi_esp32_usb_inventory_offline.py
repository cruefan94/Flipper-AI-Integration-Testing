"""Offline, public-safe USB inventory triage. No device access or flashing."""
import re
import unittest

PORT = re.compile(r"^/dev/(ttyUSB|ttyACM)[0-9]{1,3}$")
USB_ID = re.compile(r"\b([0-9a-fA-F]{4}):([0-9a-fA-F]{4})\b")
KNOWN_BRIDGES = {"10c4:ea60": "CP210x", "1a86:7523": "CH340", "0403:6001": "FT232", "303a:1001": "Espressif USB"}
SECRET = re.compile(r"(?i)(token|password|secret|api[_-]?key|authorization|bearer)")
MAX_INPUT = 8192

def triage(lsusb_text, ports_text):
    """Classify user-provided command output, never enumerate live hardware."""
    if not isinstance(lsusb_text, str) or not isinstance(ports_text, str):
        raise ValueError("text required")
    if len(lsusb_text) + len(ports_text) > MAX_INPUT:
        raise ValueError("input too large")
    if SECRET.search(lsusb_text + ports_text):
        raise ValueError("potential credentials: do not share logs")
    ids = sorted(set(":".join(m).lower() for m in USB_ID.findall(lsusb_text)))
    ports = sorted(set(p for p in re.findall(r"/dev/[^\s]+", ports_text) if PORT.fullmatch(p)))
    bridges = sorted(set(KNOWN_BRIDGES[i] for i in ids if i in KNOWN_BRIDGES))
    return {
        "usb_bridges": bridges,
        "serial_ports": ports,
        "status": "candidate_ports_present" if ports else "no_candidate_serial_port",
        "warning": "USB IDs and ports alone do not prove ESP32 presence, ownership, bootloader access or electrical safety",
    }

class OfflineTriageTests(unittest.TestCase):
    def test_cp210x(self):
        r = triage("Bus 001 Device 003: ID 10c4:ea60", "/dev/ttyUSB0")
        self.assertEqual(r["usb_bridges"], ["CP210x"])
        self.assertEqual(r["serial_ports"], ["/dev/ttyUSB0"])
    def test_ch340(self):
        self.assertEqual(triage("ID 1a86:7523", "/dev/ttyUSB2")["usb_bridges"], ["CH340"])
    def test_s2(self):
        self.assertEqual(triage("ID 303a:1001", "/dev/ttyACM0")["usb_bridges"], ["Espressif USB"])
    def test_no_port(self):
        self.assertEqual(triage("ID 10c4:ea60", "")["status"], "no_candidate_serial_port")
    def test_reject_untrusted_paths(self):
        self.assertEqual(triage("", "/dev/ttyS0 /dev/ttyUSB0;rm")["serial_ports"], [])
    def test_secret(self):
        with self.assertRaises(ValueError): triage("Authorization: Bearer abc", "")
    def test_size(self):
        with self.assertRaises(ValueError): triage("x"*8193, "")
    def test_no_false_esp32_claim(self):
        self.assertIn("do not prove ESP32", triage("ID 0403:6001", "/dev/ttyUSB1")["warning"])

if __name__ == "__main__":
    unittest.main()
