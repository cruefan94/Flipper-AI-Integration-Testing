# Flipper AI — project ecosystem and integration index
_Last inventory: 2026-11-13. Repository index, NOT a statement that code is merged or devices work._

The Flipper Zero AI Momentum + Android AI Satellite project is coordinated as one ecosystem while preserving the security and build boundaries of independent repositories. The owner's designated MAIN ChatGPT conversation is the planning hub, but ChatGPT chats are not automatically moved/synced; GitHub code and documented decisions remain traceable in the individual repositories.

## Known repositories

| Repository | Responsibility | Boundary |
| --- | --- | --- |
| [Flipper-AI-Momentum-](https://github.com/cruefan94/Flipper-AI-Momentum-) | Private primary Momentum firmware, BLE AI1 and ESP32-S2 source, private project roadmap | No private source/secrets in public CI |
| [Flipper-AI-Android-Satellite](https://github.com/cruefan94/Flipper-AI-Android-Satellite) | Android companion/APK and local/online/hybrid AI, BLE, voice and radio | App build/phone testing there |
| [Flipper-AI-Integration-Testing](https://github.com/cruefan94/Flipper-AI-Integration-Testing) | This public-safe CI / integration contract workspace | Tests only; no automatic flashing or production release |
| [Flipper-AI-Battery-Optimizer](https://github.com/cruefan94/Flipper-AI-Battery-Optimizer) | Separate private battery read-only advice/telemetry prototype | Not integrated with live app/firmware; explicit approval needed |
| [Flipper-AI-Civic-Companion.](https://github.com/cruefan94/Flipper-AI-Civic-Companion.) | Private future 2021 Civic / Galaxy A52 Android Auto experiment | Deferred until verified core; no main source changes |
| [Flipper-AI-Mascot-Library](https://github.com/cruefan94/Flipper-AI-Mascot-Library) | Public optional approved AI Dolphin animation concept | New mascot work requires owner preview approval |
| [Flipper-AI-Momentum-Community](https://github.com/cruefan94/Flipper-AI-Momentum-Community) | Private community-based independent scaffold | No unreviewed import into main |
| [Flipper-AI-Momentum.](https://github.com/cruefan94/Flipper-AI-Momentum.) | Empty private similarly named repo | Not the authoritative source; do not mistake for Flipper-AI-Momentum- |

Private repository links may require authorization. Non-Flipper repositories are intentionally excluded.

## Current core delivery scope

- Working Android local inference using a compatible existing model/runtime; secure user opt-in cloud processing with transparent hybrid fallback.
- BLE-first Momentum/Flipper ↔ Android AI1 protocol with consent, bounded frames and hardware/device verification; later Wi-Fi/USB-C transport options.
- Android usable app navigation and version-safe updates; voice/PTT and read-only radio streaming; ESP32-S2 and safe practical diagnostics.
- Build/test evidence before release; a branch, prototype, CI fixture or user's reported APK success does not in itself prove complete product delivery.

## Future ideas retained, not silently activated

1. **Battery optimizer:** local battery recommendations and read-only telemetry; separate approval, real device tests and measured results required.
2. **2021 Civic companion:** Galaxy A52 wired Android Auto with BLE to Flipper; explicitly deferred until core work is done.
3. **Mascot library:** approved AI Dolphin sequences and future compatibility/packaging; no unapproved designs.
4. **Raspberry Pi 4B with qFlipper:** later device testing after owner is ready to set up Pi.
5. **Phone USB SDR and advanced radio:** optional receiver, lawful public feeds, transcription/signal identification and future Flipper attachment.
6. **Future alternative transports, firmware practical apps and licensed UI packs:** experimental until independently reviewed/verified.

## Integration guardrails

- **No automatic private-public mirroring.** Reviewed public-safe fixtures only; public Actions cannot be assumed to access private repo.
- **No automatic firmware merging or cross-repo deployment.** Work on explicit branches, review compatibility, signing and licensing.
- **No unauthorized active transmissions or vehicle control.** All radio features initially receive-only.
- **No secrets or private logs.** Never publish Cloudflare/Gemini credentials, device tokens, signing keys, private sources or personal data.
- **No false completion claims.** Record separate source, CI, phone, Flipper and end-to-end evidence.
- Maintain separate repositories for side-project concepts until separately approved integration.

For detailed internal roadmap and decision history, authorized collaborators can consult [the private project hub](https://github.com/cruefan94/Flipper-AI-Momentum-/blob/main/docs/UNIFIED_PROJECT_HUB.md). Reference this page from the other seven repositories to keep the ecosystem discoverable.
