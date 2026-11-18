"""Read-only first-generation Pironman configuration/status snapshot.

No subprocesses, GPIO access, service writes, or privileged commands.
Run: python3 raspberry_pi/pironman_readonly_snapshot.py --self-test
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

FIELDS = {
    "temp_unit": ("C", "F"),
    "screen_always_on": ("True", "False"),
    "rgb_switch": ("True", "False"),
    "rgb_style": ("breath", "leap", "flow", "raise_up", "colorful"),
}
NUMBERS = {"fan_temp": (30, 80), "screen_off_time": (0, 86400),
           "rgb_blink_speed": (0, 100), "rgb_pwm_freq": (400, 1600)}
COLOR = re.compile(r"^[0-9a-fA-F]{6}$")

def parse_config(content: str) -> dict:
    """Parse an untrusted config as data, never as executable code."""
    if len(content) > 65536:
        raise ValueError("configuration too large")
    values = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if key not in FIELDS and key not in NUMBERS and key != "rgb_color":
            continue
        if key in values:
            raise ValueError("duplicate recognized setting")
        if key in FIELDS:
            if value not in FIELDS[key]:
                raise ValueError("invalid setting")
            values[key] = value
        elif key in NUMBERS:
            if not re.fullmatch(r"[0-9]{1,5}", value):
                raise ValueError("invalid numeric setting")
            number = int(value)
            low, high = NUMBERS[key]
            if not low <= number <= high:
                raise ValueError("setting out of range")
            values[key] = number
        else:
            if not COLOR.fullmatch(value):
                raise ValueError("invalid RGB color")
            values[key] = value.upper()
    return values

def snapshot(path: Path) -> dict:
    # Avoid symlinks and non-regular files; never write configuration.
    import stat
    st = path.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_size > 65536:
        raise ValueError("unsupported configuration file")
    # This is advisory monitoring, not a security boundary against a hostile
    # concurrent local process; no privileged file reads are attempted.
    return parse_config(path.read_text(encoding="utf-8"))

def self_test() -> None:
    sample = ("temp_unit = C\nfan_temp = 40\nscreen_always_on = True\n"
              "screen_off_time = 60\nrgb_switch = True\nrgb_style = colorful\n"
              "rgb_color = 4682B4\nrgb_blink_speed = 100\nrgb_pwm_freq = 1600\n")
    assert parse_config(sample)["fan_temp"] == 40
    assert parse_config(sample)["rgb_color"] == "4682B4"
    for bad in ("fan_temp = 20", "rgb_color = $(whoami)",
                "rgb_style = rainbow", "fan_temp = 40\nfan_temp = 50"):
        try:
            parse_config(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid config accepted")
    assert parse_config("unknown_setting = anything") == {}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--config", type=Path,
                        default=Path.home() / ".config/pironman/config.txt")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test passed")
    else:
        print(json.dumps(snapshot(args.config), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
