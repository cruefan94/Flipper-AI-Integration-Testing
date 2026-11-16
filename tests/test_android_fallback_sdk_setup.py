"""Prevent public-safe Android fallback regressions to obsolete SDK setup."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ci-fallback-verify.yml"


class AndroidFallbackSdkTests(unittest.TestCase):
    def test_fallback_uses_hosted_sdk_instead_of_obsolete_tools_package(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("android-actions/setup-android@v3", text)
        self.assertIn('Missing preinstalled Android SDK on hosted runner', text)
        self.assertIn("sdkmanager --version", text)

    def test_android_build_keeps_required_sdk_packages_and_gates(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('sdkmanager --install "platforms;android-35" "build-tools;35.0.0"', text)
        self.assertIn("Reproduce Android source preflight and host tests", text)
        self.assertIn(":app:assembleDebug --no-daemon --stacktrace", text)
        self.assertIn("NO PHONE/BLE HARDWARE VERIFIED", text)


if __name__ == "__main__":
    unittest.main()
