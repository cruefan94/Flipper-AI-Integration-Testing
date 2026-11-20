#!/usr/bin/env python3
"""Offline ESP32 boot-strap observation validator. No GPIO, serial or flashing access."""
import json
import sys

VALID = {"esp32-wroom", "esp32-s2"}
STATES = {"low", "high", "unknown"}

def assess(record):
    if not isinstance(record, dict) or set(record) != {"board", "en", "gpio0", "supply_v", "external_5v_gpio"}:
        raise ValueError("Expected exact offline observation fields")
    board, en, gpio0 = record["board"], record["en"], record["gpio0"]
    v, unsafe = record["supply_v"], record["external_5v_gpio"]
    if board not in VALID or en not in STATES or gpio0 not in STATES:
        raise ValueError("Invalid board or pin observation")
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 5.5:
        raise ValueError("Invalid measured supply")
    if not isinstance(unsafe, bool):
        raise ValueError("Invalid GPIO hazard flag")
    hazards = []
    if unsafe: hazards.append("5V_ON_3V3_GPIO")
    if not 3.0 <= v <= 3.6: hazards.append("SUPPLY_OUTSIDE_NOMINAL_3V3_RANGE")
    if en == "low": hazards.append("CHIP_HELD_IN_RESET")
    if "unknown" in (en, gpio0): hazards.append("PIN_OBSERVATION_INCOMPLETE")
    mode = "ROM_DOWNLOAD_STRAP_POSSIBLE" if en == "high" and gpio0 == "low" else "NOT_CONFIRMED"
    return {"board_hint_unverified": board, "boot_mode_hint": mode, "hazards": hazards,
            "flash_authorized": False, "device_access": False,
            "notice": "GPIO0 is sampled at reset; observations alone cannot prove ROM mode or board wiring."}

def selftest():
    base = {"board":"esp32-wroom","en":"high","gpio0":"low","supply_v":3.3,"external_5v_gpio":False}
    assert assess(base)["boot_mode_hint"] == "ROM_DOWNLOAD_STRAP_POSSIBLE"
    assert not assess(base)["flash_authorized"]
    assert assess({**base,"board":"esp32-s2"})["board_hint_unverified"]=="esp32-s2"
    assert assess({**base,"en":"low"})["boot_mode_hint"]=="NOT_CONFIRMED"
    assert "CHIP_HELD_IN_RESET" in assess({**base,"en":"low"})["hazards"]
    assert assess({**base,"gpio0":"high"})["boot_mode_hint"]=="NOT_CONFIRMED"
    assert "5V_ON_3V3_GPIO" in assess({**base,"external_5v_gpio":True})["hazards"]
    assert "SUPPLY_OUTSIDE_NOMINAL_3V3_RANGE" in assess({**base,"supply_v":5.0})["hazards"]
    assert "PIN_OBSERVATION_INCOMPLETE" in assess({**base,"gpio0":"unknown"})["hazards"]
    for bad in ({**base,"supply_v":True},{**base,"board":"esp32-c3"},
                {**base,"external_5v_gpio":"no"},{**base,"gpio0":"grounded"}):
        try: assess(bad)
        except ValueError: pass
        else: raise AssertionError("invalid observation accepted")
    print("12 offline safety assertions passed")

if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        selftest()
    elif len(sys.argv) == 1:
        raw = sys.stdin.read(8193)
        if len(raw) > 8192: raise SystemExit("Input too large")
        print(json.dumps(assess(json.loads(raw)), indent=2))
    else:
        raise SystemExit("Usage: python esp32_boot_safety.py [--self-test]")
