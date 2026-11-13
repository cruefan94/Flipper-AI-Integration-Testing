# Flipper AI: Android-first encrypted firmware delivery

## Status and scope

The public CI run [#43347240367](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43347240367) successfully built the custom Momentum source and uploaded the **encrypted** updater artifact. This is **not** evidence of a successful boot, BLE pairing, or Android AI inference on hardware. Do not flash without a recovery plan.

The public artifact is a GitHub Actions ZIP containing `flipper-ai-updater.tar.gz.enc`, encrypted with AES-256-CBC, PBKDF2, 250,000 iterations and a random salt. The encryption passphrase is stored as GitHub Actions secret `FLIPPER_ARTIFACT_PASSPHRASE`; it is not recoverable from GitHub. Do not post it or put it in repository files.

## Download on Android

1. Open the successful [GitHub Actions run](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43347240367) while signed in.
2. Under **Artifacts**, download **encrypted-flipper-ai-updater**. Unzip the downloaded GitHub ZIP. You should see `flipper-ai-updater.tar.gz.enc`.
3. **Do not rename the encrypted file to .tgz and do not send it to the Flipper app.** It is not an installable firmware update.
4. Decryption requires a trusted tool supporting OpenSSL `enc -aes-256-cbc -pbkdf2 -iter 250000`. On a trusted desktop with OpenSSL installed, run:
   ```sh
   openssl enc -d -aes-256-cbc -pbkdf2 -iter 250000 -salt \
     -in flipper-ai-updater.tar.gz.enc -out flipper-ai-updater.tar.gz
   ```
   OpenSSL prompts for the passphrase. Never pass the passphrase on the command line or paste it into chat.
5. Extract `flipper-ai-updater.tar.gz` using a trusted archive manager, preserving the updater folder hierarchy.
6. Review `SHA256-manifest.json` inside the archive. For each file in the updater folder, calculate SHA-256 and compare it with the manifest's recorded digest. If any digest or size differs, **stop**.
7. Back up the Flipper SD card and save a known-working official/Momentum recovery image before attempting installation.
8. Do not attempt to flash until the updater format is confirmed for the target Flipper hardware, and device-side boot/recovery checks are planned.

## Android-only limitation

The current artifact is encrypted with OpenSSL's command-line format. The official Flipper mobile app cannot install this encrypted archive directly. An Android-only user needs a trustworthy OpenSSL-compatible decryption environment or a dedicated reviewed decryptor. **Do not install random APKs that ask for the passphrase.** A separate Android-friendly delivery process is still needed.

## Security and release limitations

- GitHub Actions artifacts in this public repository can be downloaded by people with repository access; the archive is encrypted but not access-controlled as a private release.
- The firmware source is checked out transiently from the private repository and is not uploaded to the public artifact.
- AES-CBC encryption does not authenticate ciphertext. Verify the extracted updater files against the manifest, and treat both manifest and ciphertext as untrusted until provenance is independently established. For stronger future releases, use authenticated encryption and a signed manifest with a separately trusted public key.
- Successful CI compilation is not a hardware validation. Experimental AI BLE GATT and Android interoperability remain unverified.
- Artifact retention is seven days; rerun the workflow if it expires.
