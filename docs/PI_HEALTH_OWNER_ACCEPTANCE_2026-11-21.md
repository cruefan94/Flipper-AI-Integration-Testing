# Raspberry Pi 4B / first-generation Pironman: owner-controlled health monitor acceptance

Status: **documentation-only, not device validated**. Side project; no firmware or Android release dependency. Source candidate: [Pi health PR #294](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/294), head `308e08e599c9f670bb9a3a05d280ed476fe0a314`. Exact-head synthetic regression [44907699661](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44907699661) passed; public-safe smoke [44907699579](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44907699579) passed. These do **not** validate Pi hardware.

## Preconditions and stop conditions
- Owner explicitly consents to run the candidate script on the **actual Pi**, after reviewing it. Obtain source from the reviewed PR only; verify the expected commit. Do not download and execute unreviewed scripts.
- Leave the currently functioning first-generation Pironman fan, RGB, OLED, services and startup configuration untouched. Do not stop/restart services, install packages, invoke sudo, write GPIO/I²C or change permissions.
- Keep cooling functional. Stop if temperature rises unexpectedly, cooling stops, output is malformed, or Pi performance degrades.
- Never publish full device inventory, serial numbers, addresses, tokens, or unredacted diagnostic logs to a public repository.

## Read-only acceptance procedure (owner runs locally)
1. Confirm normal fan/OLED behavior visually **before** the test; do not alter settings. In the checked-out source tree, inspect `raspberry_pi/pi_health_readonly.py`.
2. From that tree, run one snapshot: `python3 raspberry_pi/pi_health_readonly.py --once`. No sudo, network, GPIO, USB or service control is required.
3. Expect a single JSON line containing `status: read_only`, `hardware_control: false`, `memory_bytes`, three finite nonnegative `load_averages`, and optional `temperature_c` (null is permitted if inaccessible). `MemAvailable <= MemTotal` and memory values are nonnegative.
4. Only after separately consenting to repeated sampling, run `python3 raspberry_pi/pi_health_readonly.py --watch --consent` and observe **three** consecutive samples approximately ten seconds apart. End with Ctrl+C. The interval is a sampling cadence, not an OLED refresh claim.
5. Check fan/OLED behavior again and confirm no settings changed. Record only pass/fail, source commit, number of samples and a coarse temperature range, **not** raw logs or device identifiers.
6. If any check fails, stop and preserve the existing installation; report sanitized symptoms in a private issue. Do not run automatic repair, update, or flash.

## Acceptance matrix
| Check | Required evidence | Current result |
|---|---|---|
| Python syntax + synthetic sanity regression | Exact-head Actions run | PASS for PR #294 commit above |
| Single-shot kernel metrics | Owner's actual Pi observation | NOT RUN |
| Explicit-consent 10-second sampling | Three local samples, no background daemon | NOT RUN |
| Pironman cooling/OLED unaffected | Owner before/after observation | NOT RUN |
| Flipper/ESP32 read-only telemetry | Separately approved contracts and devices | NOT IMPLEMENTED |
| qFlipper backup/recovery | Separate owner-controlled acceptance | NOT RUN |

## Integration and release gates
- Pi monitor is optional, standalone and read-only. Do not infer AI1 BLE/USB gateway compatibility or include it in Android APK / native F7 .tgz from these tests.
- Maintain the existing two-consecutive-failure workflow/branch rule. A second completed failure (or repeated pre-runner failure) requires the approved PUBLIC-SAFE fallback; private Actions:read 403 means **BLOCKED**, not successful failover. Record original/fallback run IDs.
- Only the integration-testing owner may update the combined candidate ledger; no protected-branch merge, production deploy, device flash, or replacement of the signed Android app.
