# Encrypted native fallback: evidence and release HOLD (2026-11-20 13:02 ET)

## Scope and provenance
- Approved public-safe fallback workflow run: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44782522608
- Workflow ref: public integration-testing main at `f1cac80854f26259534c032b2855dd609dd6c58e`; event `workflow_dispatch`; title references private failure `Flipper-AI-Momentum-#44672962932`.
- GitHub job `firmware / custom-firmware` completed successfully, including private source retrieval, upstream Momentum clone, private overlay/unit tests, native custom Momentum compile, archive verification, encryption, and encrypted artifact upload.
- Run artifact metadata: `encrypted-flipper-ai-mobile-native-tgz-UNTESTED` (12,650,072 bytes), uploaded 2026-11-20 17:32 UTC. **Do not publish, download to public storage, decrypt in public CI, or redistribute.**
- The separate fallback https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44782519310 completed public diagnostics only; firmware job **skipped**. It is not evidence of a firmware build.

## Unresolved promotion gates
1. Privately establish exact private firmware source SHA and upstream Momentum SHA used in run #44782522608; public run HEAD is **not** the private source SHA.
2. Verify actual `firmware.dfu` suffix and CRC against the extracted native updater, not only synthetic fixtures; verify archive contents, per-file SHA-256, encrypted delivery provenance and reproducible source-to-artifact identity in an authorized private environment.
3. Verify C2 boundary and qFlipper recovery instructions; never retry the previously failed CRC 9-99 updater.
4. Verify Android APK installed-app signer, package ID, increasing versionCode, and owner-approved opt-in test install; no replacement or uninstall.
5. Require paired BLE AI1 contract/version and hardware acceptance. Pi/ESP32 remain optional until accepted.
6. Preserve two-failure trigger by workflow+branch; distinguish host diagnostics, native build, and hardware flash. HTTP 403 on private Actions history remains BLOCKED until explicitly rechecked; a manually dispatched fallback does not prove the automatic monitor has permissions.

**Disposition: encrypted native fallback build evidence exists; release candidate and hardware flash remain HOLD.** No private source, binary, keys, token, logs or personal diagnostics included here.
