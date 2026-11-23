# Cross-project release evidence intake — 2026-11-23 04:03 ET

**Public-safe test-only checklist. Not a release authorization.** Private firmware source, updater binaries, APKs, credentials, serial numbers, device logs, certificate private keys, and personal diagnostics must never be uploaded here.

## Exact-head evidence record (one record per artifact)

| Field | Required evidence | Failure disposition |
|---|---|---|
| component / feature | Named FAP, F7, Android, Pi/ESP32 module | UNKNOWN => HOLD |
| repository / PR / branch | Exact canonical links | Missing => HOLD |
| full source SHA | 40 hexadecimal characters, same SHA as CI | Mismatch => HOLD |
| workflow + run ID + job name | Completed job on exact source SHA | skipped/pending/failed => HOLD |
| artifact name / version / SHA-256 | Private-only manifest for F7 and APK; publish only sanitized digest if authorized | Missing => HOLD |
| protocol contract | AI1 BLE API version, request/response and timeout/error behavior, both sides tested | Mismatch => HOLD |
| dependency / optional peripheral | Required model, firmware, board and runtime versions | Unknown => HOLD |
| hardware acceptance | Explicit owner-approved test evidence, never inferred from CI | Missing => HOLD |

## Native F7 artifact validation (private authorized environment only)

1. Identify the **actual** generated `firmware.dfu` inside the exact native `.tgz`, not a synthetic fixture. Verify DFU suffix length, signature, and CRC using an independent verifier; store the verifier version and output privately.
2. Compute SHA-256 of the archive and each updater member from the same immutable run. Bind those hashes to the full source SHA, native job and run ID in the **private** release ledger.
3. Confirm artifact provenance and encryption-only transfer; never attach the native binary or raw private logs to a public issue, PR, or workflow.
4. Reject the known DFU CRC 9-99 image categorically. A passing compiler job, synthetic CRC fixture or generic smoke test does not override this quarantine.
5. Document official Momentum/qFlipper recovery and SD backup before any proposed physical test. **Do not flash without explicit owner approval.**

## Android non-destructive upgrade gate

1. Record the installed app's package ID, versionCode and signing certificate SHA-256 privately, without copying personal app data.
2. Compare with the exact CI APK's package ID, versionCode, signing certificate fingerprint and APK SHA-256.
3. In-place update is eligible only if package ID and signing lineage match and versionCode is valid. A mismatch means **HOLD**; never uninstall/replace the existing app.
4. A separate test package must use an intentionally distinct application ID, be opt-in, and must not silently alter the stable app's data.
5. Verify offline model loading, opt-in cloud behavior, and physical AI1 BLE separately; a green build is not hardware acceptance.

## Mandatory two-failure fallback ledger

Record for each workflow+branch: ordered failed run IDs, exact SHAs, completion timestamps, runner provisioned? (yes/no), failed step category (source/test/runner/permissions/unknown), fallback eligibility, authorized public-safe fallback workflow and dispatch ID, exact private source pin, fallback job outcomes, skipped jobs, and corrective next action.

Trigger on **two consecutive completed failures** or repeated pre-provisioning failure. Do not conflate different workflows. If private Actions:read is 403 or missing, record **BLOCKED—PERMISSION**, no fabricated fallback ID. Never publish private source, firmware, keys, tokens, binaries or raw logs. Do not loop reruns or weaken gates.

## Current scoped evidence, not release approval

- Momentum PR #89 full-build failures: [45124987882](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124987882), [45124990592](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124990592). Second run's Worker and Python jobs failed; native stages skipped. **Fallback eligibility triggered; new dispatch unverified.**
- Historical native F7 scoped job [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328): job success, **artifact-level CRC/hash and physical test not established**.
- Historical scoped fallbacks [45097671207](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45097671207), [45097674197](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45097674197), and [45097676662](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45097676662) do not jointly establish end-to-end compatibility.
- Android [PR #143](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/143) M7 checks and [PR #146](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/146) Worker correction are isolated evidence; signer continuity and combined exact-head candidate remain HOLD.

Owner of combined release candidate ledger: integration-testing workstream only. No production merge, install, flash, deploy, or promotion authorized by this document.
