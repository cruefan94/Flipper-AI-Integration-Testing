"""Source guards for Flipper's strictly read-only staged-firmware review."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
MANAGER=(ROOT/"esp32-expansion/flipper/esp_manager.c").read_text()
STAGER=(ROOT/"hardware-installer/verify_bundle.py").read_text()

class SdPlanGuards(unittest.TestCase):
    def test_menu_and_fixed_staging_path(self):
        self.assertIn('"Review staged SD firmware"',MANAGER)
        self.assertIn("EspReviewSdPlan",MANAGER)
        self.assertIn('"/ext/apps_data/esp_flasher/flipper-ai-esp32-plan.txt"',MANAGER)
        self.assertIn('sidecar="flipper-ai-esp32-plan.txt"',STAGER)

    def test_read_only_small_and_overflow_bounded(self):
        m=MANAGER.split("static void esp_review_sd_plan(",1)[1].split(
            "static void esp_send(",1)[0]
        self.assertIn("storage_file_open(file, ESP_SD_PLAN_PATH, FSAM_READ, FSOM_OPEN_EXISTING)",m)
        self.assertIn("length<=ESP_SD_PLAN_LIMIT",m)
        self.assertIn("if(!n) break;",m)
        self.assertIn("data[got]=0;",m)
        self.assertIn("furi_record_close(RECORD_STORAGE)",m)
        for forbidden in ("storage_file_write(", "storage_file_remove(",
                          "esp_loader_flash", "furi_hal_serial_tx(", "bt_ai_satellite_send("):
            self.assertNotIn(forbidden,m)

    def test_board_families_must_match_and_staging_is_not_an_authorization(self):
        m=MANAGER.split("static void esp_review_sd_plan(",1)[1].split(
            "static void esp_send(",1)[0]
        self.assertIn("BOARD=esp32_wroom32_devkit|CHIP=esp32",m)
        self.assertIn("BOARD=flipper_wifi_devboard_s2|CHIP=esp32s2",m)
        self.assertIn("HW_UNVERIFIED=1",m)
        self.assertIn("SD_COPY_ONLY|ESP_FLASHER_APPROVAL_REQUIRED",m)
        self.assertIn("STAGED FIRMWARE - REVIEW ONLY",m)
        self.assertIn("Owner approval in ESP Flasher is required",m)

if __name__=="__main__":unittest.main()
