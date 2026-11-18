# Paired AI1 build execution evidence — 2026-11-18 11:04 EST

PUBLIC-SAFE metadata-only integration handoff. No private firmware source, binary, keys, personal diagnostics, or release authorization.

## Exact heads and job execution

| Component | Exact head | Actions run | Executed job | Result | Gate |
|---|---|---|---|---|---|
| Momentum AI1 CCCD authenticated subscription tests, PR #59 | `27fdfcc565db2c23f058faac934cef0ca31a865d` | [44337640102](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44337640102) | source overlay checks | success | source only |
| Momentum AI1 F7 candidate, PR #59 | `27fdfcc565db2c23f058faac934cef0ca31a865d` | [44337640519](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44337640519) | quick source checks success; **full F7 compile skipped; native TGZ publishing skipped** | workflow success | **NO F7 candidate promotion** |
| Android AI1 reconnect/discovery tests, PR #74 | `8eca68fd72acbea116b0cb2b84e0f2815e4d7940` | [44340028689](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44340028689) | host regressions, debug APK build, provenance and artifact upload | success | **DEBUG-UNTESTED; NO automatic upgrade** |
| Historical encrypted F7 run | different historical pinned revision, not paired with these heads | [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) | private custom-firmware compile and encrypted artifact upload | success | not current-source evidence |

**Contract acceptance:** Compare Android #74 and Momentum #59 at exact SHAs for AI1 UUIDs, authenticated CCCD subscription ordering, reconnect and session revocation, notification framing, request/response semantics and RPC-vs-AI1 separation. A green source test is not a BLE hardware handshake. Run public synthetic protocol tests only on public data; keep firmware-specific contract checks and logs in approved private routes.

**F7 release stop:** Prior C2 overlap and DFU CRC 9-99 remain blockers. Require non-skipped native F7 compile and TGZ packaging at exact promoted source SHA, private memory-layout/C2 guard pass, **real** firmware.dfu suffix CRC check (not synthetic-only), TGZ and component SHA-256, encrypted-only artifact identity and qFlipper recovery plan. Never retry CRC 9-99 artifact; never bypass C2 guard; physical flash requires owner approval.

**Android release stop:** Keep current installed app untouched. Verify installed-vs-candidate signer certificate, package ID, versionCode monotonicity and data-preserving upgrade path before any upgrade. Debug APK is opt-in only after owner approval; no automatic install.

**Fallback:** Preserve two completed failures on the same workflow and branch (or repeated pre-provision failure) as trigger; record exact failure run IDs and corresponding approved public-safe fallback dispatch ID, private access/403 classification and per-job outcomes. Historical fallback [44288673073](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44288673073) had firmware job success, but trigger attribution remains unresolved. Never infer release safety or billing failure from workflow color.

**Integration ledger:** Both coordinated deliverables remain HOLD. Pi/ESP32/Arduino/radio/voice are optional until independent compatible, safe tested provenance is supplied. No candidate branch modified by this handoff.

Next: private firmware owner provide exact non-skipped C2-safe F7 job and CRC/hash attestation; Android owner provide signer/versionCode comparison; integration owner run paired AI1 contract checks and record the exact refs in the sole candidate ledger.