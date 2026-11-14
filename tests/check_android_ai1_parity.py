"""Compare published virtual BLE GATT contract against real public Android source."""
import pathlib
import re
import sys

EXPECTED = {
    "SERVICE": "c8c7ab10-6355-4ea8-a76a-0a4a64de0001",
    "RX": "c8c7ab10-6355-4ea8-a76a-0a4a64de0002",
    "TX": "c8c7ab10-6355-4ea8-a76a-0a4a64de0003",
}

def check(source):
    for name, uuid in EXPECTED.items():
        pattern = r"public\s+static\s+final\s+UUID\s+" + name + r"\s*=\s*UUID\.fromString\(\"([0-9a-f-]+)\"\)"
        matches = re.findall(pattern, source)
        if matches != [uuid]:
            raise ValueError(f"{name} expected {uuid}, got {matches}")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_android_ai1_parity.py <BleSatellite.java>")
    check(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    print("Real Android AI1 service/RX/TX UUIDs match virtual contract")
