# Raspberry Pi 4B / first-generation Pironman — read-only monitor acceptance (draft)

Status: **procedure only; NOT physically executed or accepted**. This is a Pi-side optional component, not a firmware or Android release candidate.

## Scope and preconditions
- Raspberry Pi 4B (4 GB), Raspberry Pi OS, first-generation Pironman. Preserve existing working fan, RGB, OLED and services.
- Only run on the owner's Pi after owner opt-in. No sudo, package install, service restart, GPIO/I2C/SPI writes, OLED updates, firmware flash, USB reset or network discovery.
- The monitor reads only `/proc/meminfo` and `/proc/uptime`; other sources (OLED, Flipper, ESP32) remain **unknown** without independent verified read-only adapters.
- Stop if CPU temperature or fan behavior appears abnormal. Never use this monitor to replace the existing fan controller.

## Stage A — offline code acceptance (CI, no Pi)
- Pin the exact head SHA of the tested branch. Verify the eight-test tick workflow and public-safe smoke workflow against that SHA, not merely a previous parent.
- Confirm no skips; inspect `raspberry_pi/pi_monitor_tick.py`, `pi_monitor_adapter.py`, `pi_proc_collector.py`, `pi_monitor_freshness.py` and associated tests.
- Confirm consent false never calls the collector, consent revocation resets sample timestamp, a regressed clock does not sample, 9.99 seconds does not sample, 10.00 seconds does, and exceptions become unknown rather than healthy.
- Document exact Actions URLs, run IDs, commit, source provenance and any failures. After two completed failures on the same workflow/branch, apply the approved public-safe fallback without copying private source or logs. Permission 403 means BLOCKED, not success.

## Stage B — owner-approved live read-only acceptance (NOT YET DONE)
1. Owner confirms fan and OLED are operating normally before starting; record baseline observations without changing settings.
2. In a normal, unprivileged Pi terminal, optionally inspect these **read-only** values:
   ```sh
   cat /proc/uptime
   grep -E '^(MemTotal|MemAvailable):' /proc/meminfo
   ```
3. Owner explicitly enables monitoring in the future UI; no background monitor is started by this document. The host UI supplies `time.monotonic()` and invokes `monitor_tick(consent=True, now_seconds=..., last_sample_at=...)` only after consent.
4. Compare two consented samples at least 10 seconds apart against the two read-only kernel files. Confirm that an earlier tick does not sample and that revocation prevents further reads.
5. Disconnect or omit Flipper/ESP32 inputs: their status must remain **unknown**, not online, healthy or verified. Pironman OLED state is likewise unknown unless separately read-only verified.
6. Observe that fan cooling, RGB, OLED, Pi services and qFlipper behavior are unchanged. If not, stop and investigate independently.
7. Capture a redacted test report: Pi OS version, observed sample intervals, consent off/on/off outcomes, cooling observation, error cases, and exact source commit. **Do not record serials, credentials, IP addresses, pairing tokens or personal paths.**

## Acceptance gate
Only label **physical Pi read-only acceptance passed** when an owner-supplied device report confirms consent behavior, real sample results, cooling unchanged, and reproducible commit/CI provenance. Offline CI alone never meets this gate.

## Related Pi-side workstream ledger
| Workstream | State / next gate |
|---|---|
| Pironman control center | Design only until first-generation interface is identified; reversible settings, rollback and physical cooling acceptance required |
| 10-second Pi monitor | Offline tick tests passed on prior head; live acceptance pending |
| OLED / Flipper / ESP32 monitor | Unknown until independently validated read-only inputs |
| Pi OS low-memory/browser cleanup | No automatic deletion; design safe preview and rollback |
| qFlipper USB diagnostics / backup | Read-only diagnostics first; owner-led backup/restore verification |
| Pi-local AI | Existing runtime, local-first, resource limits and opt-in |
| Phone-to-Pi remote access | Off by default; authenticated, encrypted, opt-in |
| BLE/Wi-Fi/USB gateways | Separate optional Pi builds; contract and security acceptance pending |

## Release handoff
Do not promote this documentation or monitor into Android test APK or F7 Momentum updater. Integration-testing owns the combined release ledger. Preserve the existing F7 DFU CRC 9-99 no-retry restriction and Android signing-mismatch no-replacement restriction. No production or protected-main merges.
