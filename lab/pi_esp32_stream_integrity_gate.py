"""Read-only bounded local ESP32 image verification. Synthetic fixtures only in public CI.

Never invokes esptool, GPIO, serial, or flashing. Hash match is not authenticity.
"""
import hashlib
import os
import stat
from pathlib import Path
from pi_esp32_flash_manifest_gate import inspect_manifest, MAX_IMAGE_BYTES

def inspect_local_image(manifest, image_path):
    metadata = inspect_manifest(manifest)
    errors = list(metadata["errors"])
    if not metadata["valid_metadata"]:
        return {"image_integrity_verified": False, "flash_authorized": False, "errors": errors}
    if not isinstance(image_path, (str, Path)) or not str(image_path):
        return {"image_integrity_verified": False, "flash_authorized": False, "errors": ["image_path"]}
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(image_path, flags)
    except (OSError, ValueError, TypeError):
        return {"image_integrity_verified": False, "flash_authorized": False, "errors": ["image_open"]}
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode):
        os.close(fd)
        return {"image_integrity_verified": False, "flash_authorized": False, "errors": ["image_not_regular"]}
    try:
        with os.fdopen(fd, "rb") as stream:
            if info.st_size == 0 or info.st_size > MAX_IMAGE_BYTES:
                errors.append("image_size_limit")
            elif info.st_size != manifest["image_bytes"]:
                errors.append("image_size_mismatch")
            else:
                h = hashlib.sha256()
                count = 0
                while True:
                    chunk = stream.read(min(65536, MAX_IMAGE_BYTES + 1 - count))
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > MAX_IMAGE_BYTES or count > manifest["image_bytes"]:
                        errors.append("image_changed_or_oversize")
                        break
                    h.update(chunk)
                if not errors and count != manifest["image_bytes"]:
                    errors.append("image_size_mismatch")
                if not errors and h.hexdigest() != manifest["image_sha256"]:
                    errors.append("image_hash_mismatch")
    except OSError:
        errors.append("image_read")
    return {"image_integrity_verified": not errors, "flash_authorized": False, "errors": errors}
