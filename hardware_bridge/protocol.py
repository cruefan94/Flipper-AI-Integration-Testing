"""Public-safe v1 device-envelope and stream framing *contract*.

No transport connections, authentication, device execution, or remote shell.
Existing Flipper AI1 BLE frames are a DIFFERENT transport with a 180-byte limit.
"""

from __future__ import annotations

import json
import re
from typing import Any

VERSION = 1
MAX_JSON_BYTES = 4096
TARGETS = frozenset(("pi", "android", "flipper", "p4", "wroom32", "uno", "termux"))
ACTIONS = frozenset((
    "device.ping", "device.status", "device.capabilities",
    "telemetry.read", "script.list", "script.request"
))
SCRIPT_TARGETS = frozenset(("pi", "termux"))
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$")
_SCRIPT_ID = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


class ProtocolError(ValueError):
    """Malformed or disallowed public bridge message."""


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolError("Duplicate JSON key")
        result[key] = value
    return result


def _check_structure(value: Any, depth: int = 0) -> None:
    """Bound container nesting and values before passing to any adapter."""
    if depth > 5:
        raise ProtocolError("Args nesting too deep")
    if isinstance(value, dict):
        if len(value) > 32:
            raise ProtocolError("Too many argument keys")
        for key, item in value.items():
            if not isinstance(key, str) or len(key) > 64:
                raise ProtocolError("Invalid argument key")
            _check_structure(item, depth + 1)
    elif isinstance(value, list):
        if len(value) > 32:
            raise ProtocolError("Too many array elements")
        for item in value:
            _check_structure(item, depth + 1)
    elif isinstance(value, str):
        if len(value) > 1024:
            raise ProtocolError("Argument string too long")
    elif value is None or type(value) in (bool, int, float):
        pass
    else:
        raise ProtocolError("Unsupported argument type")


def validate_envelope(message: Any) -> dict[str, Any]:
    """Validate schema, *not* the identity/permissions of the sender."""
    if not isinstance(message, dict):
        raise ProtocolError("Envelope must be an object")
    required = {"version", "kind", "request_id", "source", "target", "action", "args"}
    missing = required - message.keys()
    unexpected = message.keys() - (required | {"status"})
    if missing or unexpected:
        raise ProtocolError("Missing or unexpected envelope fields")
    if type(message["version"]) is not int or message["version"] != VERSION:
        raise ProtocolError("Unsupported protocol version")
    if message["kind"] not in ("request", "response"):
        raise ProtocolError("Unsupported message kind")
    if not isinstance(message["request_id"], str) or not _IDENTIFIER.fullmatch(message["request_id"]):
        raise ProtocolError("Invalid request ID")
    if message["source"] not in TARGETS or message["target"] not in TARGETS:
        raise ProtocolError("Unknown source/target")
    if message["source"] == message["target"]:
        raise ProtocolError("Source and target must differ")
    if message["action"] not in ACTIONS:
        raise ProtocolError("Unsupported action")
    if not isinstance(message["args"], dict):
        raise ProtocolError("Args must be an object")
    _check_structure(message["args"])
    if message["kind"] == "request":
        if "status" in message:
            raise ProtocolError("Request cannot carry status")
        if message["action"] == "script.request":
            if message["target"] not in SCRIPT_TARGETS:
                raise ProtocolError("Script target must be Pi or Termux")
            args = message["args"]
            if not {"script_id"} <= args.keys() or args.keys() - {"script_id", "params"}:
                raise ProtocolError("Only an approved script ID and params are allowed")
            if not isinstance(args["script_id"], str) or not _SCRIPT_ID.fullmatch(args["script_id"]):
                raise ProtocolError("Invalid script ID")
            if "params" in args and not isinstance(args["params"], dict):
                raise ProtocolError("Script params must be an object")
    elif message.get("status") not in ("ok", "error"):
        raise ProtocolError("Response requires ok/error status")
    return message


def encode_envelope(message: dict[str, Any]) -> bytes:
    validate_envelope(message)
    try:
        payload = json.dumps(
            message, ensure_ascii=False, separators=(",", ":"), sort_keys=True,
            allow_nan=False
        ).encode("utf-8")
    except (ValueError, TypeError, OverflowError) as exc:
        raise ProtocolError("Invalid JSON value") from exc
    if len(payload) > MAX_JSON_BYTES:
        raise ProtocolError("Envelope too large")
    return payload


def decode_envelope(payload: bytes) -> dict[str, Any]:
    if not isinstance(payload, bytes) or not payload or len(payload) > MAX_JSON_BYTES:
        raise ProtocolError("Invalid envelope length")
    try:
        message = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_no_duplicate_keys,
            parse_constant=lambda x: (_ for _ in ()).throw(ProtocolError("Invalid JSON constant"))
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("Invalid UTF-8 JSON") from exc
    validate_envelope(message)
    # Also enforce the same canonical size and number rules as the writer.
    encode_envelope(message)
    return message


def encode_stream_frame(message: dict[str, Any]) -> bytes:
    """For controlled UART/TCP test adapters only (NOT Flipper AI1 GATT)."""
    payload = encode_envelope(message)
    return len(payload).to_bytes(2, "big") + payload


def decode_stream_frame(frame: bytes) -> dict[str, Any]:
    if not isinstance(frame, bytes) or len(frame) < 3:
        raise ProtocolError("Incomplete frame")
    expected = int.from_bytes(frame[:2], "big")
    if expected == 0 or expected > MAX_JSON_BYTES or len(frame) != expected + 2:
        raise ProtocolError("Invalid stream length")
    return decode_envelope(frame[2:])
