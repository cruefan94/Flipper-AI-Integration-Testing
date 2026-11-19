# Android PR89 recovery: exact-head evidence and candidate hold (2026-11-19 18:01 EST)

Public-safe coordination record; no firmware source, device identifiers, private logs, APK or credentials.

## Exact evidence

- Failed Android PR88 head `38d1c48ff38cc3feeb7f3f75bee2edd9a405274a`: [run 44622613821](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44622613821), completed failure in host regressions.
- New Android PR89 head `c6e83950428476afe7d8c29c0f60400ac19b7b03`: [PR89](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/89), [run 44632497713](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44632497713), completed success. Source/JVM/security regressions, debug APK build, fail-closed integrity/provenance and artifact upload all succeeded.
- This is a **new branch**, not a second consecutive failed run on PR88's exact workflow+branch. Do not count the earlier PR88 failure against PR89 or claim that PR88's own head passed.
- Success establishes a CI-built **debug** APK, not an upgrade-compatible signed release. No signer certificate comparison to the installed app or safe versionCode upgrade proof was obtained.
- Native Momentum [PR71](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/71) remains failed at exact head `238a54bfc0b1708a827d489cee5d43197871bfb3`, runs [44568518970](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568518970) and [44568544991](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568544991).
- Public-safe fallback [44587016728](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44587016728) passed **diagnostics only**; native firmware, Android and contract jobs skipped. It does not clear the F7 C2 audit.
- Older native encrypted F7 [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) completed successfully at its historical ref, not at PR71 head. Never retry the CRC 9-99 updater.

## Next acceptance gates

1. Android owner: supply debug APK artifact digest, package ID, versionCode, signing certificate fingerprint and installed-app signing fingerprint through a **private** evidence route; compare signer and versionCode before any upgrade path is proposed. No install or uninstall.
2. BLE AI1: pin both exact Android and Momentum source SHAs and protocol version, execute cross-side HELLO/ACK, malformed frame, reconnect, background, stale callback and consent tests; separate host tests from physical handshake.
3. F7 owner: privately identify failing PR71 C2 step, authoritative flash boundary, real firmware.dfu UFD suffix CRC, archive/internal SHA-256 and encrypted-only provenance. No public binaries or logs.
4. Integration-testing owner: update the single candidate ledger only with exact matching passing native artifacts and compatibility evidence. Public smoke green does not imply release approval.
5. qFlipper/Termux: read-only backups, recoverability and redacted diagnostics; do not automate flashing or publish personal paths/identifiers.

**Promotion: HOLD** for both unified Android test APK and native F7 .tgz. No protected merges, hardware flashing, installs or deployment authorized.
