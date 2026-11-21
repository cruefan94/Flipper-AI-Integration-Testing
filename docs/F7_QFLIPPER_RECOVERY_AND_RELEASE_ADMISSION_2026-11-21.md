# Flipper F7 qFlipper recovery and release admission (public-safe checklist)

Status: **documentation only / NOT FLASH APPROVAL**. This page contains no private firmware, hardware logs, credentials, or private diagnostics.

## Absolute exclusions
- Never retry the updater that failed the real DFU CRC **9-99** check.
- A passing synthetic CRC fixture, successful GitHub Actions job, encrypted archive SHA-256, or presence of a `.tgz` does **not** prove the internal `firmware.dfu` CRC or device compatibility.
- Do not uninstall or replace the existing Android Satellite app if its signer differs. A separately identified test package is opt-in only.
- Do not flash a user's Flipper, install an APK, merge protected branches, or publish decrypted private binaries without explicit owner approval.

## Evidence gate before any owner-authorized F7 test
1. In the **private** build context, pin the exact firmware source commit, upstream Momentum revision, overlay revision, workflow URL and run ID, artifact ID, build target (F7), and SDK/toolchain revision.
2. In the same private context, decrypt only into an access-controlled temporary directory. Inspect the real `.tgz` manifest and required files; reject missing, duplicate, unexpected, or path-traversal entries.
3. Independently calculate SHA-256 of the decrypted updater archive and its contained `firmware.dfu`; record private attestation linking both hashes to the encrypted artifact ID and source commit. Never substitute the GitHub artifact ZIP hash for the updater hash.
4. Validate the **actual** DFU suffix structure, signature, declared suffix length and CRC32 over the real `firmware.dfu` bytes using an independent verifier; record the tool and exit status privately. Reject missing or mismatched suffixes. Synthetic fixtures are unit tests only.
5. Verify Momentum updater metadata, hardware target, manifest and package structure with the pinned compatible tooling. Require a fresh, clean native compile and artifact verification. Confirm no original Momentum functions were intentionally removed.
6. Maintain a **private** recovery manifest: exact known-good official Momentum release, official download source, current Flipper firmware version, qFlipper version, backup location, backup restore plan and owner-approved test window.
7. Release admission remains **HOLD** until provenance, internal hashes, genuine DFU CRC, recovery rehearsal, API/AI1 parity, and explicit device-owner approval are documented. Device acceptance is separate from CI.

## Owner-operated recovery preparation (no flashing implied)
- Use the official qFlipper application and official Momentum release channel only; verify the intended firmware source before use.
- Before any future authorized test, back up user data and SD-card contents, and confirm that backups can be read. Do not share device serials, pairing secrets, or personal diagnostics publicly.
- Keep the known-good official Momentum package and qFlipper recovery documentation available offline. Ensure a reliable USB data cable and adequate device power.
- If a future authorized update fails, **stop retrying the failing custom package**. Preserve the error category privately, consult official Flipper/qFlipper recovery instructions, and restore only with owner approval. Do not assume a failed update means permanent damage.
- After any authorized recovery, verify normal boot, storage visibility, existing Momentum functions and BLE pairing before considering a new candidate. Never declare recovery successful from CI alone.

## Two-failure CI routing
- Count **completed** failed attempts per exact repository + branch + workflow. Pending/skipped attempts do not count; failures on different branches must not be combined.
- After two consecutive completed failures, or repeated failure before a job is provisioned, invoke only the approved **public-safe encrypted/private-firmware fallback route** in the integration-testing workspace.
- Record source run IDs, fallback dispatch/run ID, observed outcome and corrective action. A green monitor without verified private Actions visibility is not a successful fallback.
- Private Actions:read HTTP 403 or missing authorization is **BLOCKED**, not a billing diagnosis. Never copy private source, plaintext binaries, tokens or raw private logs to public CI.

## Integration handoff fields
`component | repo | branch | exact SHA | dependency SHAs | workflow/run URL | artifact ID | artifact SHA-256 scope | internal updater SHA-256 (private) | real DFU CRC result (private) | AI1 contract version | signing/update status | recovery evidence | hardware status | release gate`

Historical reference only: native encrypted workflow [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328); public synthetic regression [43828565939](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828565939). Neither alone authorizes flashing.

Coordination: [private Phase 1 release blockers](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23), [test-only fallback coverage](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23), [canonical private tracker](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5).
