# AI1 session-matrix evidence and native F7 release hold — 2026-11-18 14:03 ET

Public-safe metadata only. No firmware source, binary, credential, device log or personal diagnostics.

## Exact evidence
- Firmware PR [#61](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/61), branch `test/ai1-session-boundary-matrix-20261118-1332`, SHA `eb4ce27cbd3728e557d2f70c574b88862989bcfb`.
- [Host session-boundary tests #44370998030](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44370998030) succeeded. [Overlay #44370998011](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44370998011) succeeded.
- [F7 candidate #44370997639](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44370997639) workflow concluded success, **but** job `Full F7 AI1 firmware compile and strict update inspection` (135037421310) was **skipped** and native TGZ release job (135037423049) was **skipped**. Only quick source checks (135037418315) succeeded. This is **not** a native F7 acceptance.
- Android PR [#75](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/75), SHA `f4c60535788bd18b74b6888facae001d9eb3676a`, [combined host APK workflow #44361989778](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44361989778) succeeded. Candidate signing compatibility with installed APK and safe versionCode upgrade remain unverified.
- [Integration smoke #44365118829](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44365118829) succeeded at PR #138's head.
- Historical encrypted native [#43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) custom-firmware job succeeded at a **different** revision; cannot substitute for exact current SHA, real DFU suffix CRC, C2 overlap clearance and TGZ SHA-256 verification.

## Candidate acceptance matrix
| Gate | Evidence required | Status |
| --- | --- | --- |
| Firmware F7 | Non-skipped native compile + TGZ; C2 safety; actual DFU suffix CRC; private SHA-256/provenance; qFlipper restore instructions | HOLD |
| Android | Signed test APK with exact SHA/versionCode; installed-versus-candidate signer compatibility or explicitly separate app ID; data-safe upgrade plan | HOLD |
| BLE AI1 | Exact paired API/version, ATT/GATT/CCCD auth/session matrix, phone-to-device handshake and disconnect/reconnect tests | HOLD: independent host tests only |
| Pi/ESP32/radio/voice | Explicit compatibility, safety and integration tests | Optional/not promoted |
| Fallback | Two completed consecutive failures same workflow+branch or repeated pre-job failure; approved public-safe dispatch; exact trigger/run attribution and permissions; no private artifacts published | Preserve; historical attribution unresolved |

## Follow-up / non-negotiable protections
Firmware owner must address C2 overlap without bypassing guards and run a **non-skipped** native candidate at exact SHA. Never retry the known DFU CRC 9-99 updater. Android owner must compare signing certificate digests and versionCode before proposing any upgrade; do not uninstall or replace installed app. Integration owner must pair firmware/Android protocol revisions and run contract tests, maintain sole shared release ledger, and capture fallback dispatch metadata. A successful workflow with skipped release jobs is not a release candidate. No flashing, installation, protected merge, production deployment, or public private-firmware distribution without explicit owner approval.
