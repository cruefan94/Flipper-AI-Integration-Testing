"""Public-safe release evidence admission gate; validates metadata, never reads private artifacts.

A passing CI job is not proof of a flashable F7 updater or a safe APK upgrade.
This module deliberately fails closed on missing artifact-specific evidence.
"""
import re

SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")


def validate_candidate(record):
    """Return machine-readable blockers; [] only for complete metadata evidence.

    The caller must separately authenticate evidence and perform device tests.
    No actual firmware or APK is accepted or distributed by this function.
    """
    blockers = []
    if not isinstance(record, dict):
        return ["candidate record must be an object"]
    if record.get("kind") not in ("android_apk", "momentum_f7"):
        return ["unknown candidate kind"]
    if not COMMIT.fullmatch(str(record.get("source_sha", ""))):
        blockers.append("exact source SHA missing")
    if not SHA256.fullmatch(str(record.get("artifact_sha256", ""))):
        blockers.append("artifact SHA-256 missing")
    if not record.get("build_run_url", "").startswith("https://github.com/"):
        blockers.append("build run link missing")
    jobs = record.get("required_jobs")
    if not isinstance(jobs, dict) or not jobs or any(v != "success" for v in jobs.values()):
        blockers.append("required job missing, skipped or unsuccessful")
    if record["kind"] == "android_apk":
        if not SHA256.fullmatch(str(record.get("signer_cert_sha256", ""))):
            blockers.append("APK signer fingerprint missing")
        if record.get("upgrade_signer_match") is not True:
            blockers.append("installed APK signer compatibility unverified")
        if record.get("ble_ai1_contract_passed") is not True:
            blockers.append("BLE AI1 contract parity unverified")
    else:
        if record.get("real_firmware_dfu_crc_verified") is not True:
            blockers.append("real firmware.dfu CRC unverified")
        if not SHA256.fullmatch(str(record.get("firmware_dfu_sha256", ""))):
            blockers.append("firmware.dfu SHA-256 missing")
        if record.get("encrypted_only_delivery") is not True:
            blockers.append("encrypted-only artifact handling unverified")
        if record.get("qflipper_recovery_documented") is not True:
            blockers.append("qFlipper recovery evidence missing")
    return blockers
