"""Pure offline ESP32 image-byte integrity gate; no file, serial, GPIO or flash I/O.

Only public-safe synthetic byte buffers should be used in public CI.
A matching hash does not establish firmware authenticity, board compatibility,
owner consent or permission to flash.
"""
import hashlib

from pi_esp32_flash_manifest_gate import inspect_manifest


def inspect_image_bytes(manifest, image):
    """Compare exact supplied bytes against validated manifest, fail closed."""
    metadata = inspect_manifest(manifest)
    errors = list(metadata["errors"])
    if not isinstance(image, bytes):
        errors.append("image_type")
    elif len(image) == 0:
        errors.append("image_empty")
    elif len(image) > 16 * 1024 * 1024:
        errors.append("image_limit")
    elif isinstance(manifest, dict):
        expected_size = manifest.get("image_bytes")
        if type(expected_size) is int and len(image) != expected_size:
            errors.append("image_size_mismatch")
        digest = manifest.get("image_sha256")
        if type(digest) is str and len(digest) == 64 and all(c in "0123456789abcdef" for c in digest):
            if hashlib.sha256(image).hexdigest() != digest:
                errors.append("image_hash_mismatch")
    return {
        "valid_metadata": metadata["valid_metadata"],
        "image_integrity_verified": metadata["valid_metadata"] and not errors,
        "flash_authorized": False,
        "errors": errors,
    }
