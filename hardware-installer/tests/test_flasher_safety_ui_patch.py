"""GPL ESP Flasher patch: explicit owner confirmation and safe OTG power state."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from patch_esp_flasher_verify import (
    patch_flash_confirmation, patch_switch_confirmation, patch_power_policy,
    PatchMismatch,
)

BROWSE="""        if(app->num_selected_flash_options) {
            // only start next scene if at least one option is selected
            scene_manager_next_scene(app->scene_manager, EspFlasherSceneConsoleOutput);
        }"""
START="""void esp_flasher_scene_start_on_enter(void* context) {
}
        } else if(event.event == SubmenuIndexEspFlasherSwitchA) {
            app->switch_fw = SwitchToFirmwareA;
            scene_manager_next_scene(app->scene_manager, EspFlasherSceneConsoleOutput);
            consumed = true;
        } else if(event.event == SubmenuIndexEspFlasherSwitchB) {
            app->switch_fw = SwitchToFirmwareB;
            scene_manager_next_scene(app->scene_manager, EspFlasherSceneConsoleOutput);
            consumed = true;"""
POWER="""    uint8_t attempts = 0;
    bool otg_was_enabled = furi_hal_power_is_otg_enabled();
    while(!furi_hal_power_is_otg_enabled() && attempts++ < 5) {
        furi_hal_power_enable_otg();
        furi_delay_ms(10);
    }
    furi_delay_ms(200);
    if(furi_hal_power_is_otg_enabled() && !otg_was_enabled) {
        furi_hal_power_disable_otg();
    }"""

class SafetyUIPatchTests(unittest.TestCase):
    def test_image_flash_requires_separate_yes_and_cancel_does_not_launch(self):
        c=patch_flash_confirmation(BROWSE)
        self.assertIn("CONFIRM ESP FLASH",c)
        self.assertIn('dialog_message_set_buttons(confirm, "Cancel", NULL, "FLASH")',c)
        self.assertIn("dialog_message_show(app->dialogs, confirm)",c)
        self.assertIn("if(choice == DialogMessageButtonRight)",c)
        self.assertIn("External USB power",c)
        self.assertLess(c.index("if(choice == DialogMessageButtonRight)"),
                        c.index("scene_manager_next_scene("))
        with self.assertRaises(PatchMismatch):
            patch_flash_confirmation(c)

    def test_ota_boot_flag_writes_require_separate_positive_consent(self):
        c=patch_switch_confirmation(START)
        self.assertIn("CONFIRM OTA WRITE",c)
        self.assertIn('dialog_message_set_buttons(confirm, "Cancel", NULL, "WRITE")',c)
        self.assertIn("return choice == DialogMessageButtonRight;",c)
        self.assertEqual(c.count("if(flipper_ai_confirm_ota_write("),2)
        self.assertEqual(c.count("app->switch_fw = SwitchToFirmware"),2)
        with self.assertRaises(PatchMismatch):
            patch_switch_confirmation(c)

    def test_never_auto_enable_or_disable_otg_on_external_usb_board(self):
        c=patch_power_policy(POWER)
        self.assertNotIn("furi_hal_power_enable_otg(",c)
        self.assertNotIn("furi_hal_power_disable_otg(",c)
        self.assertIn("external USB power",c)
        self.assertIn("3.3 V UART",c)
        with self.assertRaises(PatchMismatch):
            patch_power_policy(c)

    def test_upstream_anchor_drift_fails_closed(self):
        with self.assertRaises(PatchMismatch):
            patch_flash_confirmation(BROWSE.replace("only start next scene","changed"))
        with self.assertRaises(PatchMismatch):
            patch_switch_confirmation(START.replace("SwitchToFirmwareB","DifferentFirmware"))
        with self.assertRaises(PatchMismatch):
            patch_power_policy(POWER.replace("attempts < 5","attempts < 20"))

    def test_patch_is_computed_before_writing_any_files(self):
        code=(Path(__file__).resolve().parents[1]/"patch_esp_flasher_verify.py").read_text()
        self.assertLess(code.index("changes[path]=transform(path.read_text())"),
                        code.index("path.write_text(patched)"))
        self.assertIn('sha!=UPSTREAM_SHA',code)
        self.assertIn('"esp_flasher_worker.c":patch_text',code)
        self.assertIn('"scenes/esp_flasher_scene_browse.c":patch_flash_confirmation',code)
        self.assertIn('"scenes/esp_flasher_scene_start.c":patch_switch_confirmation',code)
        self.assertIn('"esp_flasher_app.c":patch_power_policy',code)

if __name__=="__main__":
    unittest.main()
