"""Public-safe checks for exact-private-SHA firmware build fallback.

Tests the reviewed workflow text only; no private source, credentials, network,
firmware binaries, or Flipper hardware are accessed.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
BUILD=(ROOT/".github/workflows/private-momentum-ai-build.yml").read_text()
ROUTER=(ROOT/".github/workflows/ci-fallback-verify.yml").read_text()

class ExactShaFirmwareFallbackTests(unittest.TestCase):
    def test_private_source_is_exactly_pinned_not_old_branch(self):
        self.assertIn("8201647c822896a4dbc8fe00547f94aabb633de9",BUILD)
        self.assertIn("feature/momentum-ai1-next-flash-20261117",BUILD)
        self.assertNotIn("feature/flash-test-platform-v01",BUILD)
        self.assertIn("actual=\"$(git -C \"$RUNNER_TEMP/private-ai\" rev-parse HEAD)\"",BUILD)
        self.assertIn('test "$actual" = "$EXPECTED_PRIVATE_SHA"',BUILD)
        self.assertIn("Private branch moved; exact SHA mismatch. Refuse build.",BUILD)

    def test_reusable_fallback_receives_original_source_identity(self):
        self.assertIn("source_sha: ${{ inputs.source_sha }}",ROUTER)
        self.assertIn("source_branch: ${{ inputs.source_branch }}",ROUTER)
        self.assertIn("source_sha:",BUILD)
        self.assertIn("source_branch:",BUILD)

    def test_full_firmware_and_real_dfu_gate_before_encrypted_upload(self):
        self.assertIn("./fbt TARGET_HW=7 COMPACT=1 copro_dist updater_package fap_dist -j2",BUILD)
        self.assertIn("scripts/inspect_update.py",BUILD)
        self.assertIn('"crc_verified": true',BUILD)
        self.assertIn('"flash_approved": false',BUILD)
        self.assertLess(BUILD.index("Fail closed on actual F7 firmware.dfu framing and CRC"),
                        BUILD.index("Verify native Momentum .tgz and encrypt phone-ready package"))
        self.assertLess(BUILD.index("Verify native Momentum .tgz and encrypt phone-ready package"),
                        BUILD.index("Upload encrypted firmware package only"))

    def test_private_data_never_uploaded_in_plaintext(self):
        self.assertIn("FLIPPER_PRIVATE_SOURCE_TOKEN",BUILD)
        self.assertIn("FLIPPER_ARTIFACT_PASSPHRASE",BUILD)
        self.assertIn("openssl enc -aes-256-cbc -pbkdf2 -iter 250000 -salt",BUILD)
        self.assertIn('rm -rf "$RUNNER_TEMP/firmware-delivery"',BUILD)
        self.assertIn("flipper-ai-native-tgz-delivery.tar.gz.enc",BUILD)
        self.assertIn("NOT flash-approved",BUILD)
        self.assertNotIn("upload-artifact@v4\n        with:\n          name: plaintext",BUILD)

if __name__=="__main__":
    unittest.main()
