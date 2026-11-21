# F7 encrypted artifact identity: 2026-11-21 08:00 ET

PUBLIC-SAFE evidence only. No private firmware source, binaries, keys, logs or device identifiers.

## Pinned native run
- Workflow: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328
- Status: completed / success (workflow-level only); head SHA: `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8`; branch: `fix/f7-dfu-crc-preflash-gate-20261116`.
- PR #22 current head SHA `32f631c846db67d5f581887c00bbd06599b665c6` differs from the workflow head SHA. **Do not label this run as exact-current-PR-head evidence.**
- Artifact metadata: encrypted candidate `encrypted-FlipperAI-ESP32-GATT-AUDITED-NEXT-FLASH-CANDIDATE-UNTESTED`, artifact ID `14207847319`, 12,890,755 bytes, GitHub artifact ZIP digest `sha256:1ec260e25953df1c4b637c2e7e3207d91d4318d3f0c69fac73ac974cb772807d`. Preview `encrypted-flipper-ai-esp32-integration-preview-tgz-UNTESTED`, artifact ID `14207827386`, 12,655,597 bytes, artifact ZIP digest `sha256:b55de1798c05386bbc53beddc3e59b17cda50e9094b4617365bcb5614e493e39`.
- These are GitHub **artifact archive** digests, **not** the inner native F7 `.tgz` SHA256, `firmware.dfu` CRC, or decrypted payload identity. Artifact names are ESP32-oriented and do not prove a flashable F7 updater.
- Metadata expiry: 2026-11-23 08:15:58 UTC for the named encrypted candidate and 08:15:56 UTC for preview. Retain evidence securely before expiry only through an approved private route; never mirror binaries to public.

## Private-only acceptance procedure (no flashing)
1. Pin exact private firmware source SHA and audited native build job; verify run completion and branch/commit match.
2. In approved private runner, authenticate/decrypt package without exposing it to public artifacts; inspect native F7 updater `.tgz` manifest, target board, updater files and original Momentum preservation.
3. Compute SHA-256 of the exact native updater and contained `firmware.dfu`; verify the **real** DFU suffix structure and CRC over the actual extracted file, not synthetic fixtures. Record sanitized PASS/FAIL, hash references only where approved.
4. Confirm C2 boundaries, recovery/qFlipper procedure, package identity and SD transfer checks. A green host workflow or synthetic CRC is insufficient.
5. Keep known failed CRC 9-99 updater prohibited. No flash without explicit owner approval and physical acceptance.

## Parallel Android and CI gates
- Android combined APK run #44863378694 passed at `084a7221aa7d429ac26d53c71569e32769c252af`, but current worker PR #111 is a separate branch with contract CI #44891637886, not evidence of a unified APK. Preserve installed app; compare installed and candidate signing certificate SHA-256, package ID, versionCode and data-safe upgrade before opt-in testing.
- Public CI routing classifier PR #290 at `3a00aadc6369601d4746e3a607c5533855235950` passed dedicated regression #44902197821 and smoke #44902197716. These are offline metadata tests, not proof private Actions access or fallback dispatch works.
- Existing S3 AI1 failure pair #44755541063/#44755560160 and FlipperHTTP PR #76 pair #44866082379/#44866117174 require approved private-safe fallback; if private Actions:read returns 403, mark BLOCKED, do not invent dispatch IDs or infer billing.

**Release disposition:** Android APK HOLD; native F7 updater HOLD; physical BLE AI1 UNVERIFIED; optional Pi/ESP32/radio components remain separately gated. No production merge, install or flash.
