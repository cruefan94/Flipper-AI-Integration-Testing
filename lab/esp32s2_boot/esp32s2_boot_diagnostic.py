"""Offline ESP32-S2 boot-log classifier. Never opens a device or flashes firmware."""
import re
import sys

DOWNLOAD = re.compile(r'(?i)(?:DOWNLOAD_BOOT|DOWNLOAD\s+MODE|waiting for download)')
FLASH = re.compile(r'(?i)(?:SPI_FAST_FLASH_BOOT|boot:\s*0x1[0-9a-f])')
BOOT = re.compile(r'(?i)boot:\s*0x([0-9a-f]+)')

def classify(log: str) -> str:
    if not isinstance(log, str) or not log.strip():
        return 'NO_LOG'
    if len(log) > 65536:
        return 'INVALID_LOG'
    # ESP32-S2 ROM log format varies by ROM revision.
    if DOWNLOAD.search(log):
        return 'DOWNLOAD_MODE_INDICATED'
    if FLASH.search(log):
        return 'NORMAL_FLASH_BOOT_INDICATED'
    if BOOT.search(log):
        return 'BOOT_MODE_UNKNOWN'
    return 'INCONCLUSIVE'

if __name__ == '__main__':
    # Accept pasted log from stdin only, never a serial device path.
    print(classify(sys.stdin.read(65537)))
