# ESP32 / Pi peripheral evidence handoff — 2026-11-18

Scope: **public-safe, documentation-only lab checkpoint**. No device access, radio transmission, flashing, firmware binary, private logs or secrets.

## Existing isolated prototype references (NOT CI-qualified)
| Component | Ref | Evidence missing |
|---|---|---|
| WROOM ROM log classifier | `lab/esp32-rom-boot-log-offline-20261117` @ `aca1e3cf4f338fd4bc03e37fddfc8079c8db8751` | exact-commit Actions run; real UART boot trace |
| S2 ROM log classifier | `lab/esp32s2-rom-boot-offline-20261117-2128` @ `ef4d1133a6f6879bc3754a3c53c8fc69d8a2de00` | exact-commit Actions run; S2 USB/UART boot trace |
| EN/BOOT trace validator | `lab/esp32-reset-sequence-offline-20261117-2325` @ `cf654899aabd7ab76b39957c4d184055f283168f` | exact-commit Actions run; real reset capture |
| Pi flashing preflight | `lab/esp32-pi-flash-preflight-20261117-2225` @ `5ef39b0042a93ebf57149a3107f31eb509c10c36` | exact-commit Actions run; non-destructive Pi serial discovery |
| Transport compatibility | `lab/peripheral-transport-contract-20261117-1819` @ `341961106571ac957482d65c0432165c0450c166` | exact-commit Actions run; device capability confirmation |

These refs are historical handoff references, **not proof of current branch presence or passing CI**. Resolve each SHA and inspect source before any reuse.

## Consolidated non-destructive acceptance sequence
1. Verify exact GitHub branch HEAD, tree contents and source provenance; check for overlaps with the existing Pi serial-ownership/USB identity utilities.
2. Run the **committed** tests from that exact SHA offline. Record command, exit code, fixture count and SHA; local equivalent tests do not qualify as exact-commit CI.
3. Verify exact SHA in GitHub Actions with run ID and conclusion. A missing PR-triggered run does **not** prove no push run. If Actions history is HTTP 403, mark BLOCKED, never PASS.
4. On the owner's Pi **only with separate authorization**, identify stable `/dev/serial/by-id` path and chip with read-only discovery; never auto-reset, erase, or flash. Record redacted device identifiers, UART/USB boot-mode trace and voltage/power evidence separately.
5. For WROOM, distinguish ROM download mode from normal boot; for S2, do not assume WROOM UART/USB behavior or built-in BLE support. An EN/BOOT timing trace alone cannot establish ROM download mode.
6. Validate shared ground, 3.3V GPIO levels, power-source isolation, regulator capacity and backfeed prevention before backpack wiring. Never connect 5V logic directly to ESP32 GPIO.
7. Handoff only after physical and protocol gates: exact tested commit, CI URL, public-safe provenance, hardware evidence, dependencies, recovery instructions, and API/AI1 contract version. Integration-testing release-ledger owner alone promotes combined candidates.

## Two-failure CI fallback / release hold
After two **completed** consecutive failures on the same workflow+branch, or repeated failure before job provisioning, use the approved public-safe fallback route; distinguish test failure from runner failure. Never upload private firmware, binary, keys, credentials or raw private logs. Private Actions:read HTTP 403 => **BLOCKED**, requires authorized token/permissions and verified monitor run; do not infer billing.

Phase 1 review: [private release blockers PR #23](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23), [public-safe fallback PR #23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23). The failed F7 DFU CRC 9-99 updater is quarantined and must never be retried. Android signing mismatch prohibits replacing/uninstalling the existing app. No release promotion without exact passing artifact evidence and owner-approved physical tests.

## Candidate status at handoff
Android test APK: **not integrated**. F7 Momentum updater .tgz: **not integrated**. ESP32/Pi peripherals: **optional external components, blocked on CI and physical compatibility**. Vehicle integration deferred.
