# Public integration testing scope

The JSON contract is an **initial proposal**, not a claim that Flipper and Android already exchange these messages.

## CI gates
- Python contract unit tests: checks fixture structure and safe defaults only.
- Android APK CI: runs separately at https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions
- Momentum FBT / Flipper FAP / ESP-IDF builds: not yet configured in this repository.
- Physical BLE, Wi-Fi and hardware tests: not performed by public CI.

## Security
No private repository checkout, private-source mirroring, GitHub tokens or firmware binaries are included. Review licensing and history before publishing any firmware overlay.

## Next
Implement verified adapters for the **existing** wire protocol instead of replacing it with this draft schema; add independent protocol fixtures and tests, then reviewed build sources.
