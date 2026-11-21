# MAIN integration evidence handoff — 2026-11-21 14:05 ET

This is PUBLIC-SAFE metadata only. Do not add private Momentum source, binaries, job logs, credentials, Android signing material, device identifiers or diagnostic dumps.

## Verified exact-run observations

| Component | Branch / exact SHA | Run | Outcome and scope |
| --- | --- | --- | --- |
| Android combined debug APK | `test/android-navtest-suffix-guard-20261121` / `f1e7b087630777c4ac138e57e46771a27b2b5bbe` | [44931667498](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44931667498) | Completed success; debug artifact `14717684250`, expires 2026-11-28T17:45:40Z; signing continuity and hardware BLE AI1 **not attested** |
| Prior Android build | `fix/android-navtest-package-identity-20261121` / `ad0d47c94760db3819c668c0a748a527320cd42f` | [44926545670](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44926545670) | Failed; different branch, do not count with succeeding branch |
| Public integration documentation | `audit/android-green-artifact-scope-20261121-1257` / `b79601aedd4096d523b06cec7589dd7ab6a3059f` | [44932888928](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44932888928) | Smoke job completed success; not Android/F7 hardware acceptance |
| FlipperHTTP current | `fix/flipperhttp-dns-label-length-20261121-1331` / `869484d9505244715604809421ac473a7f6c51f4` | [44936047367](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44936047367) | Completed failure: checkout, C guard, isolation and runner-availability jobs failed; native FAP compile skipped. Job failure reason **unknown** without private logs |
| Native encrypted historical candidate | Pinned source SHA requires private attestation | [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) | Workflow success only; not evidence of real firmware.dfu suffix CRC or internal updater hash |

## Candidate admission gates (no promotion without evidence)

**Android:** preserve existing installation; privately compare installed package name, signing certificate SHA-256, versionCode and intended APK signing metadata; prove upgrade compatibility or use owner-approved separate application ID for opt-in testing. Verify BLE AI1 protocol/version and transport reconnect on hardware before acceptance. A green debug APK workflow alone is insufficient.

**F7:** independently validate the actual `firmware.dfu` suffix CRC and full native updater `.tgz` contents and SHA-256 in a permitted private environment; bind attestation to exact private source SHA, build run, encrypted artifact identity and compatible Momentum target. Record tested qFlipper/DFU recovery path before any owner-approved flashing. Never retry the failed CRC 9-99 image. Synthetic CRC fixtures do not attest the native image.

**CI fallback:** count only consecutive *completed* failures for the identical repo, workflow and branch; classify before-job provisioning separately. After threshold, use approved encrypted-only private-firmware route. A 403 on private Actions:read is **BLOCKED**, not successful failover. Do not copy private logs to public CI. Existing FlipperHTTP PR #76 same-branch failures [44866082379](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44866082379) and [44866117174](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44866117174) have historical encrypted fallback [44907023267](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44907023267); this does not establish FAP acceptance.

## Next owner-safe actions

1. Privately inspect FlipperHTTP #44936047367 job-step reasons; do not assume billing or retry indefinitely.
2. Capture Android APK signing/version metadata in private, without key disclosure, and compare to installed package before considering an upgrade.
3. Capture native F7 real CRC/hash/source attestation privately and update canonical private issue #5; maintain HOLD until complete.
4. Handoff exact refs and test evidence to the integration-testing release-ledger owner; no concurrent release candidate branch edits.

No production merge, flashing, installation or candidate promotion is authorized by this document.
