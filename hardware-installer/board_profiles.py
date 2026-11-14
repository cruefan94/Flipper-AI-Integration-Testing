"""Exact, conservative hardware targets for Flipper AI expansion packages.

This catalog is deliberately NOT a universal USB or GPIO auto-detector. A UART
reply, USB VID/PID, or the shape of a devboard cannot prove flash chip layout,
bootloader, voltage compatibility, or source authorization.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Board:
    id: str
    chip: str
    method: str
    flipper_flash: bool
    description: str
    warning: str

BOARD_PROFILES = {
    "flipper_wifi_devboard_s2": Board(
        "flipper_wifi_devboard_s2", "esp32s2", "esp_flasher_review",
        True, "Official Flipper Wi-Fi Developer Board (ESP32-S2-WROVER)",
        "Keep Black Magic/debug firmware unless explicitly replacing it; "
        "official update uses uFBT and a USB host. Do not use ESP32 classic images."),
    "esp32_wroom32_devkit": Board(
        "esp32_wroom32_devkit", "esp32", "esp_flasher_review",
        True, "ESP-WROOM-32 DevKit-style board (38-pin reference)",
        "Verify exact USB-UART connection, BOOT/EN wiring and flash capacity. "
        "Use ESP Flasher separately; UART0 is not the manager's UART2."),
    "arduino_uno_r3": Board(
        "arduino_uno_r3", "atmega328p", "usb_avrdude_review",
        False, "Arduino Uno R3 ATmega328P or verified compatible clone",
        "5V UART must never drive Flipper GPIO directly. Use PC/Pi USB and a "
        "verified bootloader/board definition, or a later level-shifted ISP adapter."),
    "arduino_uno_r4": Board(
        "arduino_uno_r4", "ra4m1", "not_supported",
        False, "Arduino Uno R4 Minima/Wi-Fi (Renesas RA4M1)",
        "Not an AVR Uno R3. Needs a separate supported Arduino CLI board "
        "package; no generic Flipper auto-flash support."),
}

def match(board_id: str, chip: str) -> Board:
    try:
        board = BOARD_PROFILES[board_id]
    except KeyError as exc:
        raise ValueError("Board is not explicitly supported; no target selected") from exc
    if chip != board.chip:
        raise ValueError(f"Chip mismatch for {board_id}: expected {board.chip}")
    if board.method == "not_supported":
        raise ValueError("This board currently has no installer backend")
    return board
