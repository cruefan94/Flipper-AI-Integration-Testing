"""Offline ESP32 ROM boot-log classification. Never opens ports or flashes devices."""
import re

def diagnose(log: str) -> dict:
    if not isinstance(log, str) or len(log) > 65536:
        return {"status": "invalid", "reason": "Log must be text <= 65536 characters"}
    matches = re.findall(r"boot:0x[0-9a-fA-F]+\s*\(([^)]+)\)", log)
    if not matches:
        return {"status": "unknown", "reason": "No ROM boot mode found; verify serial baud and captured reset log"}
    mode = matches[-1]
    if mode.startswith("DOWNLOAD_BOOT"):
        return {"status": "download", "reason": "ROM download mode observed; no flash operation performed"}
    if mode == "SPI_FAST_FLASH_BOOT":
        return {"status": "flash", "reason": "Flash boot observed; BOOT/GPIO0 may not be held low at reset"}
    return {"status": "other", "reason": "Unrecognized ROM mode; inspect chip-specific documentation"}
