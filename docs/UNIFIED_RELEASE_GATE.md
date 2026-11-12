# Unified Flipper AI release integration gate

This branch is the cross-repository integration checkpoint, **not** a verified final release.

## Source components
- Private firmware: `cruefan94/Flipper-AI-Momentum-`, candidate `fix/momentum-installer-preflight-v56`. Firmware source remains private; do not copy it into this public repository.
- Android app: `cruefan94/Flipper-AI-Android-Satellite`, candidate `feature/ai-engine-public-ci-v07`. This is a passing Android CI branch, not a proven compatible firmware/app pair.
- Mascots: `cruefan94/Flipper-AI-Mascot-Library`, `main`. Optional assets; must pass manifest/format and compatibility checks before packaging.
- Community: `cruefan94/Flipper-AI-Momentum-Community`, `develop/community-foundation-v01`. Documentation/extensions only until explicitly approved.
- Empty prototype `Flipper-AI-Momentum.`: excluded.

## Required release gates
1. **Source freeze:** pin immutable SHAs for both firmware and Android; no moving branches in release manifests.
2. **Firmware:** custom Momentum integrated firmware and standalone .fap compile successfully; preserve stock Momentum features.
3. **Android:** build signed or clearly labeled debug APK from matching pinned commit; run unit and emulator launch tests.
4. **Protocol:** nonzero request IDs, max 180 bytes, HELLO/ASK/ANSWER handshake and BLE UUIDs agree across codebases; run automated contract tests.
5. **BLE:** hardware pairing, CCCD notification subscription, bidirectional AI request/reply and reconnection confirmed on a real Flipper + Android phone.
6. **Extras:** optional mascots and community assets are opt-in and do not replace stock assets.
7. **Release packaging:** include only verified build artifacts, checksums, build provenance, Android install instructions and firmware installation steps.
8. **Security:** no private repository source, credentials, cloud keys or signing secrets in public artifacts.

## Current evidence / blockers (2026-11-12)
- Public upstream Momentum mntm-012 baseline compilation: CI passed, **does not verify AI overlay**.
- Public Android AI engine branch: multiple APK CI passes, **does not verify physical BLE**.
- Customized Momentum CI: failing; first actionable compiler log still needed.
- Android emulator and internal BT linkage smoke checks: pending at last inspection.
- No complete cross-device hardware verification; **do not label this a completed unified release**.

## Progress accounting
Track each component as source present / CI passed / hardware verified / release ready. Do not sum branch counts or CI runs as percentage of completed features. Keep private firmware and public Android source separate, distribute them together only after all gates pass.
