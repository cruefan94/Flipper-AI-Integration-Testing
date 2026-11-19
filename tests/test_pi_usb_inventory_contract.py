"""Public-safe, offline USB inventory contract. No device I/O or flashing."""
import re
import unittest

PORT_RE = re.compile(r"^/dev/(?:ttyUSB|ttyACM)[0-9]{1,3}$")
BRIDGES = {"10c4:ea60": "CP210x", "1a86:7523": "CH340", "0403:6001": "FT232", "303a:1001": "Espressif USB"}

def classify_inventory(lsusb, ports):
    if not isinstance(lsusb, str) or not isinstance(ports, str):
        raise ValueError("inputs must be text")
    if len(lsusb) > 16384 or len(ports) > 4096:
        raise ValueError("inventory too large")
    bridges = set()
    for line in lsusb.splitlines():
        match = re.search(r"\bID\s+([0-9a-fA-F]{4}:[0-9a-fA-F]{4})\b", line)
        if match and match.group(1).lower() in BRIDGES:
            bridges.add(BRIDGES[match.group(1).lower()])
    devices = sorted({word for line in ports.splitlines() for word in line.split() if PORT_RE.fullmatch(word)})
    if bridges and not devices:
        status = "USB_BRIDGE_WITHOUT_SERIAL_PORT"
    elif bridges and devices:
        status = "CANDIDATE_PRESENT_NOT_BOOTLOADER_VERIFIED"
    elif devices:
        status = "SERIAL_PORT_WITHOUT_KNOWN_BRIDGE"
    else:
        status = "NO_CANDIDATE"
    return {"status": status, "bridges": sorted(bridges), "ports": devices}

class InventoryContractTests(unittest.TestCase):
    def test_bridge_no_port(self):
        self.assertEqual(classify_inventory("ID 10c4:ea60", "")["status"], "USB_BRIDGE_WITHOUT_SERIAL_PORT")
    def test_bridge_with_port(self):
        self.assertEqual(classify_inventory("ID 1a86:7523", "/dev/ttyUSB0")["status"], "CANDIDATE_PRESENT_NOT_BOOTLOADER_VERIFIED")
    def test_unknown(self):
        self.assertEqual(classify_inventory("ID 1234:5678", "")["status"], "NO_CANDIDATE")
    def test_port_only(self):
        self.assertEqual(classify_inventory("", "/dev/ttyACM0")["status"], "SERIAL_PORT_WITHOUT_KNOWN_BRIDGE")
    def test_reject_command_like_path(self):
        self.assertEqual(classify_inventory("ID 10c4:ea60", "/dev/ttyUSB0;rm")["ports"], [])
    def test_size_limit(self):
        with self.assertRaises(ValueError):
            classify_inventory("x" * 16385, "")
    def test_no_bootloader_claim_without_port(self):
        self.assertNotIn("VERIFIED", classify_inventory("ID 10c4:ea60", "")["status"])

if __name__ == "__main__":
    unittest.main()
