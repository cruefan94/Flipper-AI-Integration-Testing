# F7 Momentum updater evidence and qFlipper recovery gate (public-safe)

Status: **HOLD**. This is a reviewer checklist, not authorization to flash. Never retry the updater associated with DFU CRC 9-99. Do not publish private firmware, updater binaries, build logs, tokens, serials, device IDs, or personal diagnostics here.

## Private build evidence, recorded only in the private tracker

1. Pin the exact private firmware source commit, target F7 hardware revision, Momentum baseline, toolchain and private native Actions run ID. Record the first failing step and runner/job classification if unsuccessful. A green synthetic test is not a native firmware build.
2. Verify a **real** generated `firmware.dfu` (not a fixture): inspect its DFU suffix, signature, length and CRC with an independent parser; compare calculated CRC against the stored suffix CRC and record verifier/tool version. A CRC check alone does not establish safe flash boundaries.
3. Inspect the **actual updater archive** privately: archive member paths and types, expected updater metadata, firmware payload identity, board/target compatibility, manifest checksums, file sizes and SHA-256 of the complete .tgz and each critical member. Reject traversal paths, symlinks, unexpected files, missing members and mismatched checksums.
4. Prove the private C2/flash boundary audit passed on the **same exact** firmware image. Record the exact source SHA, native build run, artifact ID, hashes and gate results together; do not mix evidence from different commits or historical runs.
5. Confirm that the only distributable candidate route is the approved encrypted/private route. Public CI may receive only sanitized statuses, synthetic fixtures and non-sensitive run references, never a private artifact or raw private log.
6. A private release reviewer must approve the candidate before any owner-requested device test. Passing CI is not physical verification.

## Owner-controlled qFlipper recovery preparation (no automatic action)

- Before any *future explicitly approved* installation, confirm a known-good official Momentum/Flipper recovery path, a working USB data cable, sufficient power, a current compatible qFlipper installation and a readable microSD backup where applicable.
- Save the current firmware version, application settings and relevant user data by supported means **locally**; do not upload private backups or device diagnostics to public issues.
- Verify that the approved candidate's exact SHA-256 matches the privately reviewed manifest **before** opening it. Never use the prohibited CRC 9-99 artifact.
- If a future owner-approved update fails, **stop retries**. Preserve the error code and locally captured logs. Use the vendor-documented qFlipper recovery procedure with known-good firmware rather than improvising partition writes or repeating an unverified updater. Recovery is a separate owner-controlled operation; this document does not execute it.
- After recovery, check boot, SD visibility, original Momentum functions and baseline BLE/RPC separately from the custom AI1 service. Record outcomes privately; do not infer AI1 success from RPC activity.

## CI fallback accounting

Count consecutive completed failures **per workflow and branch**. At two failures, or repeated pre-job provisioning failure, invoke only the approved public-safe fallback. Record both failed run IDs and fallback run ID. If private Actions:read returns 403, label coverage **BLOCKED** and request appropriate permission configuration; a public diagnostic job passing while native compilation is skipped is not a firmware success. Do not attribute a runner failure to billing without evidence. Do not retry indefinitely or bypass gates.

## Release ledger fields

Private tracker must contain: component; exact source SHA; branch/PR; toolchain; target board; AI1 contract version; native run/job; artifact ID; SHA-256; real DFU CRC result; updater manifest verification; C2 result; recovery plan review; hardware acceptance; reviewer decision; and outstanding blockers. Android signer/package/versionCode compatibility and paired AI1 acceptance are independent HOLD gates.

Reference: private release-blocker PR #23 and public-safe failover PR #23. Historical native run #43828499328 cannot validate a newer image. This document contains no private build data.
