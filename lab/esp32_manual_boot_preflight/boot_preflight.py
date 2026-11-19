"""Offline ESP32 bootloader preflight; never opens serial ports or flashes."""
import json
import sys

CHIPS = {"esp32": "ESP32-WROOM", "esp32s2": "ESP32-S2"}

def review(payload):
    if not isinstance(payload, dict):
        return {"ready": False, "reasons": ["invalid_manifest"]}
    chip = payload.get("chip")
    reasons = []
    if chip not in CHIPS:
        reasons.append("unknown_chip")
    for field, error in (
        ("board_verified", "board_not_verified"),
        ("voltage_verified_3v3", "logic_voltage_not_verified"),
        ("common_ground_verified", "common_ground_not_verified"),
        ("serial_adapter_3v3_logic", "serial_adapter_logic_not_verified"),
        ("manual_boot_mode_confirmed", "boot_mode_not_confirmed"),
        ("board_power_off_during_wiring", "power_off_not_confirmed"),
    ):
        if payload.get(field) is not True:
            reasons.append(error)
    if payload.get("auto_reset_requested") is True:
        reasons.append("automatic_reset_not_allowed")
    if payload.get("flash_requested") is True:
        reasons.append("flashing_not_allowed")
    return {"ready": not reasons, "reasons": reasons,
            "chip_family": CHIPS.get(chip), "mode": "offline_review_only"}

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python boot_preflight.py manifest.json")
    with open(sys.argv[1], encoding="utf-8") as stream:
        payload = json.load(stream)
    print(json.dumps(review(payload), sort_keys=True))

if __name__ == "__main__":
    main()
