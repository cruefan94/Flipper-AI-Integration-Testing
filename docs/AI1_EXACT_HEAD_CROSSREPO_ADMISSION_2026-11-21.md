# AI1 cross-repository exact-head admission checkpoint — 2026-11-21 23:02 ET

Public-safe status only. No firmware source, private artifacts, credentials, signing material, personal diagnostics or logs.

## Pinned independent heads (NOT a combined candidate)

| Component | Draft PR / immutable SHA | Completed CI | Evidence limitation |
|---|---|---|---|
| Flipper standalone AI1 v0.7 | private Momentum #83 / `5024cea99a1e785cbf65f71b92990375b369fc82` | [FAP #44981324511](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44981324511) FAIL; [private F7 #44981324393](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44981324393) FAIL | FAP job and private quick-check job returned **zero steps** via authorized Actions job-step endpoint; root cause unknown; F7 compile skipped |
| Android stock RPC codec | Android #118 / `4f692a87cc569c56e3feeffd0ffbfcb2db5073c3` | [offline codec #44982398078](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44982398078) PASS; [APK #44982397889](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44982397889) PASS; [APK metadata #44982397890](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44982397890) PASS | Codec is not wired to BLE GATT AppStart/AppData transport, inference worker, reconnect, or hardware |
| Release evidence validator | integration #334 / `ec18b08bd92660e99404eadb626fd5db75014dbe` | [gate #44978748254](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44978748254) PASS; [smoke #44978748269](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44978748269) PASS | Synthetic validation is NOT exact-artifact release proof |
| Native F7 CRC prevention | integration #22 / `32f631c846db67d5f581887c00bbd06599b665c6` | [synthetic #43828565939](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828565939) PASS | Not the same head as historical [native #43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328); real firmware.dfu CRC and TGZ internal hashes NOT attested |

## Contract gate to run BEFORE candidate promotion

1. Pin the Flipper FAP build SHA and Android APK SHA in one ledger entry. Confirm stock Momentum RPC service/channel and actual AppStart -> AppState -> AppData path (not generic BLE presence or diagnostic ping).
2. Use a bounded 180-byte AI1 UTF-8 payload and deliberate BLE fragmentation; verify protobuf varint framing, ID matching, HELLO/PING/ASK response and ERROR paths, malformed frames, duplicate IDs, disconnect/reconnect, offline inference and opt-in cloud behavior.
3. Require **compiled** native FAP and compiled Android APK with exact-head workflow links; then actual device-to-device acceptance, without claiming physical success from host tests.
4. Check Android package ID, versionCode monotonicity, installed signer fingerprint compatibility (or explicitly isolated side-by-side package), and owner approval before install. Do not uninstall or replace existing app.
5. For F7 native updater require genuine extracted firmware.dfu suffix CRC, per-member hashes, archive SHA-256, exact private source provenance, encrypted-only transfer identity and a verified qFlipper backup/recovery path. Never retry known CRC 9-99 image.

## CI triage / two-failure fallback

- Treat each **workflow + branch** independently. The five failed workflows at Momentum #83 head are **not** by themselves two consecutive failures of one workflow.
- Empty step arrays for jobs `137082228274` (FAP) and `137082227979` (private quick checks) are consistent with pre-step failure, but **not proof** of billing or runner cause. Inspect authorized annotations/permissions before classifying.
- On two consecutive completed failures for the same workflow+branch, or repeated pre-provisioning failure, use the **approved public-safe private-firmware fallback route** in this integration repository. Record originating run IDs, fallback dispatch ID, outcome, and correction. A green monitoring workflow is not a dispatched fallback.
- If private Actions:read is 403/missing, mark fallback **BLOCKED**, never PASS; do not publish private source, binaries or raw logs to public Actions.
- This checkpoint changes no candidate branch, firmware source, Android source, release keys, deployment or hardware.
