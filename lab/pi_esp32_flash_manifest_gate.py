"""Offline-only ESP32 image manifest gate. Never opens a device or flashes firmware.

This checks *metadata*, not image bytes, chip identity, or owner authorization.
A passing result must never be interpreted as permission to flash.
"""
import re

SHA256 = re.compile(r"[0-9a-f]{64}\Z")
BOARDS = {"esp32-wroom-32", "esp32-s2-devboard"}
MAX_IMAGE_BYTES = 16 * 1024 * 1024
FIELDS = {"board", "board_identity_verified", "transport", "image_sha256", "image_bytes", "owner_approved"}

def inspect_manifest(data):
    """Return a fail-closed summary with no user-supplied identifiers echoed."""
    errors = []
    if not isinstance(data, dict) or set(data) != FIELDS:
        return {"valid_metadata": False, "flash_authorized": False, "errors": ["schema"]}
    if type(data["board"]) is not str or data["board"] not in BOARDS:
        errors.append("board")
    if data["board_identity_verified"] is not True:
        errors.append("board_identity")
    if data["transport"] != "usb_serial":
        errors.append("transport")
    if type(data["image_sha256"]) is not str or not SHA256.fullmatch(data["image_sha256"]):
        errors.append("sha256_format")
    if type(data["image_bytes"]) is not int or not (0 < data["image_bytes"] <= MAX_IMAGE_BYTES):
        errors.append("image_size")
    if data["owner_approved"] is not True:
        errors.append("owner_approval")
    return {"valid_metadata": not errors, "flash_authorized": False, "errors": errors}
