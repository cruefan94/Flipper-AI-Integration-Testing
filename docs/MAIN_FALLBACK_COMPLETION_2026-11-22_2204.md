# MAIN integration handoff — 2026-11-22 22:04 ET

Public-safe, metadata-only checkpoint. This is not a release approval or physical test.

## Completed automatic fallback evidence

- Monitor: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45097635063 — completed SUCCESS.
- Native encrypted firmware fallback https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45097671207 — completed SUCCESS; **firmware / custom-firmware** job succeeded, while contract/protocol/android/diagnostic jobs were skipped.
- Second native encrypted firmware fallback https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45097674197 — completed SUCCESS; **firmware / custom-firmware** job succeeded, while contract/protocol/android/diagnostic jobs were skipped.
- Protocol fallback https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45097676662 — completed SUCCESS; four protocol-integration matrix jobs succeeded, while firmware/android/contract/diagnostic jobs were skipped.
- Run titles identify triggering private workflow runs 44993155895, 44992221452 and 44981324511 respectively. Correlate exact triggering branch, consecutive failure pair and pinned source SHA through **authorized private-only evidence** before attributing cause or promoting a candidate. No private logs or source are included here.

## Latest independent gates

- Android PR #140 head `c54364fc4626abdec6ecde356678d15d60d56a9c`: combined APK #45101692363, isolated M6 #45101691816, metadata #45101691797 all completed SUCCESS. CI success is not a signer comparison or on-device inference test.
- Android PR #141 head `0ca0df1d969f6075e3b7ce3ba817d39a4a03c42a`: Worker contract #45102653725 SUCCESS; not a production Cloudflare deployment.
- Momentum PR #88 head `cf738f959de58a162a83db873bcbf66c0eac72ba`: FAP #45067246324 and F7 #45067246380 failed. Full build attempts #45067223436 and #45067233153 failed on the same branch; investigate provisioning privately, do not infer billing or source error.
- Public integration PR #397 head `62e0182dc6c3aa532048fa64b069296337363c83`: smoke #45098095439 SUCCESS.

## Candidate admission remains HOLD

1. Android: exact APK artifact SHA-256, package ID, versionCode and signing-certificate comparison with installed app; BLE AI1 physical handshake and reconnect tests. No replacement/uninstall of existing APK.
2. F7: real firmware.dfu suffix CRC, native updater archive/file hashes, encrypted-only artifact provenance, exact private source SHA, verified qFlipper recovery. Never retry known CRC 9-99 updater.
3. FAP: standalone native build evidence and compatibility with official Momentum. Firmware fallback success does **not** imply standalone FAP success.
4. Cross-component: pinned AI1 C/Java API/spec vectors, response framing/error/timeout tests, and separate Pi/ESP32 peripheral safety gates.
5. Two-failure routing: maintain workflow+branch pair accounting; dispatch only approved public-safe private runner route, record failing IDs and fallback IDs. If Actions:read is unavailable or 403, mark BLOCKED rather than claiming coverage.

No source/binary/secrets/credentials/diagnostic payloads published. No protected merges, hardware flashing, installs, production deployment or candidate promotion.
