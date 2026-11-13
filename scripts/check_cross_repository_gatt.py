#!/usr/bin/env python3
"""Public-safe, static BLE AI GATT profile compatibility checks.

Reads the experimental private Momentum GATT service and current public
Android central source from temporary CI checkouts. Publishes neither file.
This does NOT validate pairing, controller encryption, CCCD writes, or a device.
"""
import pathlib
import re
import sys


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def read(root, relative):
    path = root / relative
    require(path.is_file(), f"Required source unavailable: {relative}")
    return path.read_text(encoding="utf-8")


def expected_uuid(source, first_byte):
    match = re.search(r"#define\s+AI_UUID_BASE\(x\)\s*\{\s*x\s*,([^}]+)\}", source)
    require(match, "Missing expected byte-reversed Momentum UUID macro")
    tail = re.findall(r"0x([0-9a-fA-F]{2})\b", match.group(1))
    require(len(tail) == 15, "Momentum UUID byte count changed")
    raw = bytes([first_byte] + [int(item, 16) for item in tail])[::-1].hex()
    return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"


def check(private_root, android_root):
    private_root = pathlib.Path(private_root).resolve(strict=True)
    android_root = pathlib.Path(android_root).resolve(strict=True)
    require(private_root != android_root and private_root not in android_root.parents
            and android_root not in private_root.parents, "Source roots must be independent")
    c = read(private_root,
        "momentum_overlay/targets/f7/ble_glue/services/ai_satellite_service.c")
    session = read(private_root,
        "momentum_overlay/targets/f7/ble_glue/services/ai_satellite_session.h")
    java_prefix = "android_satellite/app/src/main/java/com/flipperai/satellite/"
    java = read(android_root, java_prefix + "BleSatellite.java")
    protocol = read(android_root, java_prefix + "SatelliteProtocol.java")
    policy = read(android_root, java_prefix + "GattProfilePolicy.java")

    for name, byte in (("SERVICE", 1), ("RX", 2), ("TX", 3)):
        match = re.search(
            r"\b" + name + r"\s*=\s*UUID\.fromString\(\"([0-9a-fA-F-]{36})\"\)",
            java)
        require(match, f"Missing Android GATT UUID {name}")
        require(match.group(1).lower() == expected_uuid(c, byte),
                f"Actual Momentum {name} UUID differs from Android")
    require(re.search(r"#define\s+AI_SVC_MAX_FRAME\s+180u\b", c),
            "Momentum AI1 GATT frame size is no longer 180")
    require(re.search(r"MAX_BYTES\s*=\s*180\b", protocol),
            "Android AI1 maximum is no longer 180")
    require(re.search(r"requestMtu\(185\)", java),
            "Android no longer requests MTU 185 for 180-byte AI1 frames")
    require(re.search(r"MIN_AI_ATT_PAYLOAD\s*=\s*32\b",
                      read(android_root, java_prefix + "TransportState.java")),
            "Minimum Android ATT handshake payload drifted")

    rx = re.search(r"\[AiCharRx\]\s*=\s*\{(.*?)\n\s*\},", c, re.S)
    tx = re.search(r"\[AiCharTx\]\s*=\s*\{(.*?)\n\s*\},", c, re.S)
    require(rx and tx, "Momentum RX/TX GATT characteristic definitions missing")
    require(".char_properties = CHAR_PROP_WRITE" in rx.group(1)
            and "ATTR_PERMISSION_AUTHEN_WRITE" in rx.group(1)
            and "AI_UUID_BASE(0x02)" in rx.group(1),
            "Momentum RX is missing authenticated GATT write contract")
    require("CHAR_PROP_NOTIFY" in tx.group(1)
            and "ATTR_PERMISSION_AUTHEN_READ" in tx.group(1)
            and "AI_UUID_BASE(0x03)" in tx.group(1),
            "Momentum TX is missing authenticated GATT notification contract")
    require("WRITE=0x08, NOTIFY=0x10" in policy,
            "Android GATT capability policy changed; re-review test")
    require("ai_sat_session_can_send(&s->session, length)" in c,
            "Momentum GATT notify no longer checks authenticated session gate")
    require("s->authenticated&&s->notifications_enabled" in session,
            "Momentum session gate no longer requires authentication and CCCD")
    print("PASS: private Momentum and current public Android GATT UUID, framing, "
          "characteristic, and source security-gate contracts")
    print("LIMIT: source audit only, not hardware BLE encryption/CCCD/MTU proof")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: check_cross_repository_gatt.py PRIVATE_FLIPPER_ROOT PUBLIC_ANDROID_ROOT")
    check(sys.argv[1], sys.argv[2])
