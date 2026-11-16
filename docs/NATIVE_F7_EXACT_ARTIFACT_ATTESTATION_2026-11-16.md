# Native F7 updater: exact-artifact acceptance record (public-safe template)

Status: **NOT ACCEPTED**. This is a procedural checklist, not a claim that any updater is safe to flash. The known DFU CRC 9-99 failed updater is permanently quarantined.

## Evidence required before promotion

Record these items **in the private canonical issue #5 only**. Never upload private firmware, encrypted delivery bytes, keys, device serials, user directories, qFlipper logs, or decrypted updater contents to this public repository.

| Gate | Required private evidence | Accept only when |
|---|---|---|
| Source provenance | Exact private Momentum commit SHA, immutable workflow run ID and attempt, build target | The native F7 build used the pinned SHA, not a moving branch |
| Native updater | Full filename, byte length and SHA-256 of the actual native `.tgz` | The downloaded file matches the private workflow manifest |
| Internal DFU | `firmware.dfu` length, suffix signature and whole-file CRC validation result | Exact extracted image passes Flipper-compatible DFU CRC gate |
| Archive contents | Safe member-name validation and expected F7 updater structure | No absolute paths, traversal, unexpected symlinks or missing required files |
| Delivery envelope | Encrypted artifact ID, immutable run/attempt, envelope hash and verification result | Public run exposes **encrypted-only** delivery; private decryption verifies authenticated contents |
| Recovery | qFlipper recovery instructions, known-good backup identity and rollback plan | Operator can restore without retrying the failed CRC 9-99 package |
| Hardware | Owner-approved physical qFlipper installation and boot results | Only after every previous gate passes and explicit owner approval |

A successful Actions job is **not** a substitute for the exact-artifact evidence. A passing synthetic CRC fixture is **not** evidence that the built `firmware.dfu` passes.

## Private-side verification procedure (never paste outputs into public CI)

1. In the private build workspace, pin the source commit SHA and workflow run **attempt**. Record the workflow and artifact IDs. Confirm all inputs and provenance from the workflow definition.
2. Obtain the encrypted-only artifact through the authorized private route. Verify the encrypted envelope SHA-256 and authenticated decryption privately; do not rely on an artifact display name.
3. Compute `sha256sum` for the decrypted updater `.tgz` and compare it with the manifest for that **same** run and attempt. Inspect archive member paths without extracting to an unsafe location.
4. Extract into a temporary private directory using safe member validation. Independently verify `firmware.dfu` suffix structure and CRC with the approved gate from public PR #22, on the **real** image, not synthetic fixtures. Record the actual checker version/commit and pass/fail privately.
5. Confirm the F7 target, required manifest/update files, hashes, and recovery plan. Keep the release status **HOLD** if any check is missing or ambiguous.
6. Separately verify Android APK package name, signing certificate fingerprint, versionCode and data-preserving upgrade compatibility; if signing differs, use only the separately identified opt-in test APK, never overwrite the owner's installed application.
7. Compare pinned firmware and Android BLE AI1 contract versions, framing/authentication/CCCD/reconnect test vectors. Host checks do not establish hardware compatibility.
8. Only after owner authorization, perform physical tests and record actual device results. Do not auto-flash or auto-install.

## Two-consecutive-failure CI fallback ledger

For each **workflow + branch** record: first completed failed run ID/attempt, second consecutive completed failed run ID/attempt (or repeated pre-job provisioning failure), failure class (**source/test**, **runner/provisioning**, **permission**, **unknown**), authorized public-safe fallback dispatch ID/attempt and result, corrective commit, and next decision.

After threshold, use the approved public-safe integration fallback. **Never** transfer private source, binaries, credentials, secrets, or raw personal logs to public. A private Actions:read HTTP 403 is **BLOCKED**, not successful fallback and not evidence of billing problems. Do not rerun indefinitely or relax checks.

## Known pinned evidence (historical, not fresh acceptance)

- Native encrypted F7 workflow: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328 — `custom-firmware` job previously reported success. Exact-image CRC attestation still missing.
- CRC regression PR #22: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22 — synthetic checks only.
- Private release blockers: https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23
- Public-safe failover coverage: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23
- Canonical private tracker: https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5

This checklist is intentionally non-executable: it must not accidentally download, decrypt, extract, install, or flash private firmware in a public workflow.
