# Cross-project CI failure classification — 2026-11-20 17:55 ET

Public-safe, read-only triage record. This is **not** firmware acceptance or a release manifest.

## Newly observed exact-head failures

| Repository / workflow | Commit | Run | Observed failing step | Classification |
|---|---|---|---|---|
| Integration-Testing / Public runner and contract smoke tests | `88c3c7023a20798f9657d266546392c3d8577b9a` (PR #253) | [44825854232](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44825854232) | `Run actions/checkout@v4` | Checkout/provisioning stage; root cause **unknown** pending safe job-log review |
| Android-Satellite / combined APK verified build | `3b039b82cd94b0bbc2921022f3e6ae3a6d8b3103` (PR #101) | [44831627893](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44831627893) | `One-time Android source, JVM and security regressions` | Host regression stage; root cause **unknown**, APK build success not established |
| Momentum / S3 AI1 exact-head host regression | `a37868b100dfdac4b575b3ff194b8e69155e9061` (PR #75) | [44755560160](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755560160) | Step detail not available from job metadata | Unclassified; paired with prior [44755541063](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755541063) |

## Immediate safe handling

1. For PR #253, inspect the checkout step's *sanitized* failure message privately. A checkout failure is not evidence of a broken AI1 contract or a GitHub billing problem. Do not count a non-executed contract test as passing.
2. For Android PR #101, request only the failing test name and sanitized exception, without personal logs, credentials or signing materials. Do not infer that the APK compiled from this run.
3. For S3 PR #75, the two completed failures trigger the owner's public-safe fallback policy. Earlier [44782519310](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44782519310) was diagnostics-only and **not** native S3 acceptance. If private Actions:read is 403, mark monitoring **BLOCKED**; do not claim successful automatic fallback.
4. Do not rerun indefinitely or weaken gates. Track run IDs and the exact branch/workflow pairing; a single failure on another workflow does not independently trigger the two-failure rule.

## Release gate invariants

- Android APK: preserve installed-app package/signing certificate and strictly compatible versionCode; never uninstall or replace the existing installation without owner approval. A separate test APK is opt-in.
- Firmware F7: never retry the CRC 9-99 updater. Native encrypted [44782522608](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44782522608) proves compilation/encrypted upload, **not** independently verified real firmware.dfu suffix CRC, internal updater SHA-256, C2 memory bounds, exact private source SHA or safe physical flashing.
- BLE AI1: stock Momentum RPC is not custom AI1 readiness; require exact contract version, stale-session invalidation and device-side acceptance.
- Pi/ESP32/radio: keep separate until real tested commit/dependencies and safe hardware acceptance are recorded.
- Do not publish private source, binary, secrets, raw device diagnostics, or decrypted firmware through the public repository.

## Next evidence needed

Sanitized first-failing error for PR #253 checkout, Android PR #101 host regressions and private S3 #75; verified permission status for private Actions:read; current F7 native updater CRC/hashes/source SHA via private route; Android installed-app certificate and candidate metadata comparison via private route. Hold unified release promotion, device flashing and app installation.
