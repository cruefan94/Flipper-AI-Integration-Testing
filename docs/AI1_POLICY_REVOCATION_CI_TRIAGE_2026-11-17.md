# AI1 policy-revocation regression: cross-project CI handoff (2026-11-17)

Public-safe metadata only. No private firmware, artifacts, tokens, user logs, or diagnostics.

## Exact observations
- Android PR [#59](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/59), head `f988d2e13b0217ccac64957705b5950fc4ec8bfc`, stacked on PR #58.
- Exact-head [Android run 44026721567](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44026721567) completed **failure**, provisioned job `133848723540`. Its host test stopped with `java.lang.AssertionError: revoked policy cannot send stale inference reply`; exit code 1. This is a **code/behavior regression**, not a pre-runner/billing failure. Do not promote its APK.
- Private Momentum PR [#41](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/41), head `1c51c08f384d5538f60580600c7c42bf1680ca1e`, exact-head [run 44024439067](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44024439067) completed failure, job `133841297676`. Job logs unavailable to this audit; **cause unconfirmed**. Prior [native trial 44023046497](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44023046497) failed real DFU header-size gate after native compile; do not assume these are identical failures.
- Public integration [PR #67](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/67) head `d84ee22f3447205e17f6d5c7e54ab8d23a4d74a7`: [smoke 44027633623](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44027633623) passed; documentation smoke is not native artifact proof.
- Older encrypted F7 [run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) job passed, but exact native DFU CRC, updater TGZ hash and source-to-artifact proof remain missing. PR #22 synthetic checks do not supply these.

## Acceptance and safe remediation
1. Android feature owner: reproduce PR #59 test deterministically; ensure revocation invalidates an in-flight ASK before notification enqueue/send; clear stale pending responses; add explicit race coverage (revocation before inference completes, during completion, and before notification), then run exact-head host tests and APK build. Avoid modifying Android source from integration-testing workstream.
2. Firmware feature owner: inspect private run #44024439067 in authorized private context, classify job failure by actual step; compare real DfuSe header declared length against emitted image bytes and validator interpretation. Never bypass header, suffix CRC, target framing or checksum gates.
3. CI fallback: count only **consecutive completed failures on the same workflow and branch** (or repeated pre-provisioning failures). For a qualifying pair, dispatch only the approved public-safe private-source route with authorized permissions, recording both failing run IDs and fallback ID. Missing dispatch permissions = **BLOCKED**; missing private Actions read (403) = **BLOCKED**, not success.
4. Integration ledger owner: pin Android/firmware exact passing commits, AI1 version/UUID/framing/CCCD authorization behavior, real firmware CRC and updater SHA-256, APK signer/package/versionCode, and restore instructions before promoting unified test candidates.
5. Preserve failed CRC 9-99 updater quarantine; protect installed Android app from incompatible signature; no protected merges, flashing, installation, or public firmware delivery.

## Release gates
- Android unified test APK: **HOLD** (PR #59 regression failure; signer and physical acceptance unverified).
- Native Momentum F7 updater: **HOLD** (exact-head CI failure; real-image integrity not established).
- BLE AI1 end-to-end, Pi/ESP32/radio: **NOT ACCEPTED** without targeted evidence.
