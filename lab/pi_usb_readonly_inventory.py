#!/usr/bin/env python3
"""Read-only Pi USB device inventory; never opens serial ports or changes devices."""
import argparse
import json
from pathlib import Path

FIELDS = ("idVendor", "idProduct", "manufacturer", "product")
def inventory(root):
    output = []
    if not root.is_dir():
        return output
    for dev in sorted(root.iterdir()):
        if not dev.is_dir():
            continue
        values = {}
        for key in FIELDS:
            path = dev / key
            try:
                values[key] = path.read_text(encoding="utf-8").strip()[:120]
            except (OSError, UnicodeError):
                values[key] = ""
        if not values["idVendor"] or not values["idProduct"]:
            continue
        output.append({"usb_path": dev.name, **values})
    return output

def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "1-1").mkdir()
        (root / "1-1" / "idVendor").write_text("303a\n")
        (root / "1-1" / "idProduct").write_text("1001\n")
        (root / "1-2").mkdir()
        (root / "1-2" / "product").write_text("incomplete")
        got = inventory(root)
        assert len(got) == 1 and got[0]["idVendor"] == "303a"
        assert got[0]["idProduct"] == "1001" and got[0]["product"] == ""
        assert "serial" not in got[0]
    assert inventory(Path("/nonexistent/read-only-usb-fixture")) == []
    print("PASS: offline USB inventory fixtures")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("/sys/bus/usb/devices"),
                        help="Read-only sysfs path, or offline fixture directory")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        print(json.dumps({"devices": inventory(args.root)}, indent=2))

if __name__ == "__main__":
    main()
