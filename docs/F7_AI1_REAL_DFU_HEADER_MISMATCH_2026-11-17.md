# Native F7 AI1 exact-source CRC gate — header mismatch incident

Audit: 2026-11-17 (public-safe; no firmware or private diagnostics attached).

## Verified run and scope
- Exact-source encrypted build trial: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44023046497
- Workflow branch: `feature/ai1-exact-sha-private-fallback-20261117`, harness SHA `10af0e2ccb2806fec76a696da6a11b9cde4eb0b4`.
- Pinned private firmware source revision: `4edfac791f9f297c8fae5e5f9cda136ff457e463` (private PR #41); this identifier is already disclosed in the public-safe PR #66 handoff. No source is reproduced.
- Actual job: `custom-firmware` (job 133836728377), completed **failure**. Private-source checkout, GATT tests, overlay application, and native F7 compile steps passed. The next step, actual native updater DfuSe framing and CRC gate, failed with **DFU header size mismatch**. Encrypted delivery/upload steps were skipped.

## Classification
This is a **post-runner artifact validation failure**, not a runner startup failure, successful updater, or proven on-device CRC fix. The gate correctly blocked delivery. The prior 9-99 failed updater is quarantined and must not be retried.

## Required targeted correction (owner of PR #66; no concurrent edits here)
1. Privately inspect the **actual** generated `firmware.dfu` bytes and the updater's expected DfuSe prefix and image-size field. Confirm which producer and verifier format definitions differ. Never dump raw binary to public logs.
2. Check whether the validator is reading the correct member of the native `.tgz` and the right byte offset, rather than relaxing the gate or rewriting a checksum to force success.
3. Add synthetic positive/negative fixtures for mismatched declared image length, truncated header, wrong target framing, corrupted suffix CRC, and a valid native sample with no private bytes.
4. Rebuild from the same pinned private SHA only after a reviewed correction; publish **only** sanitized evidence (source SHA, updater SHA-256, embedded real DFU CRC pass/fail, validator version, job/run IDs), with encrypted-only artifact delivery.
5. Preserve Android signing continuity and physical flash approval as separate gates; no flash, APK replacement, or protected merge.

## CI fallback ledger
- Previously qualifying private same-workflow failures: [43981306103](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/43981306103) and [43981327475](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/43981327475).
- The public-safe exact-source trial **did run** (44023046497), but **failed** the real DFU framing gate. This is not a successful fallback. The automated two-failure dispatch mechanism remains separately unverified; do not assert it ran.
- Do not repeat identical failed builds indefinitely. Retain same-workflow/branch counting and the BLOCKED state for missing private Actions permissions or unauthorized dispatch.
