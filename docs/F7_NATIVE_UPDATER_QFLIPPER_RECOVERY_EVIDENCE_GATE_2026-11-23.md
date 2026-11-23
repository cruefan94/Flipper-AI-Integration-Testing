# Native F7 updater and qFlipper recovery — evidence gate (2026-11-23)

PUBLIC-SAFE release review checklist. This is **not** an updater, a recovery procedure validated on hardware, or permission to flash. Never upload private firmware, updater binaries, raw logs, secrets, device identifiers or diagnostics here.

## Admission manifest (private evidence; only non-sensitive verdicts may be published)
- Pin **full 40-character firmware source SHA**, approved Momentum baseline and target F7 hardware. Match all native jobs and artifacts to that exact source.
- Record native workflow URL/run ID/job conclusion and whether its compile, packaging and CRC steps actually executed; skipped jobs are NOT PASS.
- Within the approved **private** job, inspect the **actual** `firmware.dfu` suffix: DFU suffix structure, declared length, DFU signature and CRC-32 computed over the complete DFU bytes excluding the stored CRC field, with byte order and algorithm specified. Do not substitute synthetic fixture results.
- Verify updater `.tgz` members and metadata against the approved Momentum updater format. Compute SHA-256 over the exact archive and each required member, record archive size, expected firmware target, build ref and reproducibility method in a private manifest. Compare against the downloaded artifact before any owner-authorized flash.
- Confirm artifact encryption at rest/in transit, permitted retention and **private-only** artifact access. Do not publish hashes that could identify a sensitive private build unless owner-approved.
- Verify that standalone `.fap` compatibility is independently established: a successful native F7 updater job does not prove the FAP or BLE AI1 link works.

## qFlipper recovery gate — owner-controlled only
1. Preserve a known-good **official Momentum** recovery package and its verified provenance separately from any experimental updater. Do not reuse the previously failed DFU CRC 9-99 image.
2. Before a supervised trial, document current firmware version, backup status, microSD preservation and the official qFlipper-supported recovery mode and host prerequisites. Do not collect serial numbers or personal paths in public logs.
3. Have an owner-approved rollback plan using the known-good official firmware and qFlipper's documented recovery flow. A recovery plan on paper is NOT a tested recovery.
4. After owner approval and a controlled hardware session, record installation result, normal boot, existing Momentum features, app launch, BLE AI1 round-trip, and recovery rehearsal result **privately**. If any gate fails, hold candidate and use the approved recovery procedure; never retry the quarantined CRC 9-99 updater.

## CI and release states
Use PASS only with exact-commit, exact-artifact evidence; FAIL for executed failing assertions; BLOCKED for 403/missing permissions or pre-provision runner failures; UNVERIFIED when no evidence exists. After two consecutive completed failures on the **same workflow and branch**, or repeated pre-provision failure, route only through the approved encrypted private-firmware public-safe fallback. Record triggering IDs and fallback IDs; do not attribute runner failure to billing without proof.

## Cross-project promotion hold
Android upgrade signing certificate must match the installed package or use a separately identified opt-in test package; do not uninstall/overwrite owner data. BLE AI1 version, message framing, errors, timeouts and request/response fixtures must pass C/Java contract tests at pinned commits. External Pi/ESP32 modules remain optional until accepted. No release-candidate promotion, production merge, deployment or flashing without full gate evidence and explicit owner approval.

### Evidence as of 2026-11-23 01:05 ET
- Historical native fallback: [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) workflow concluded success; **real DFU suffix CRC, archive hash and provenance not independently inspected in this checkpoint**.
- Current Momentum PR [#88](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/88) head `cf738f959de58a162a83db873bcbf66c0eac72ba`: FAP [45067246324](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45067246324) and F7 [45067246380](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45067246380) failed.
- Android PR [#143](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/143) head `c8a7c88412c2b2e961eb131502f7bba34b44014b`: combined APK [45106703969](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45106703969) succeeded, but signing continuity and device testing remain unverified.
- Integration PR [#406](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/406) smoke [45115522542](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45115522542) succeeded.
