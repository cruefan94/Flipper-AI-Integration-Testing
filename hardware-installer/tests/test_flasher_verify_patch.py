"""GPL flasher MD5 patch must reject short reads and failed verification."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from patch_esp_flasher_verify import patch_text,PatchMismatch

SOURCE=r"""// synthetic source fixture with the exact reviewed upstream transformation anchors
static esp_loader_error_t _flash_file(EspFlasherApp* app, char* filepath, uint32_t addr) {
    uint64_t size = storage_file_size(bin_file);
    loader_port_debug_print("Start programming\n");
    while(size>0) {
        size_t to_read = 1024;
        uint16_t num_bytes = storage_file_read(bin_file, payload, to_read);
        esp_loader_flash_write(payload, num_bytes);
        size -= num_bytes;
    }
    // TODO verify
    return ESP_LOADER_SUCCESS;
}

static bool _switch_fw(EspFlasherApp* app) {
    loader_port_debug_print("Preparing to set flags for firmware B\n");
    loader_port_debug_print("Finished programming\n");
    return true;
}

static void _flash_all_files(EspFlasherApp* app) {
    const int num_steps=app->num_selected_flash_options;
    int current_step = 1;
    for(int i=0;i<num_steps;i++) {
            if(err) {
                break;
            }
    }
}

static int32_t esp_flasher_flash_bin(void* context) {
        if(!_switch_fw(app)) {
            _flash_all_files(app);
        }
        app->switch_fw = SwitchNotSet;
        loader_port_debug_print(
            "Done flashing. Please reset the board manually if it doesn't auto-reset.\n");

        // auto-reset for supported boards
        loader_port_reset_target();

        // short buzz to alert user
        notification_message(app->notification, &sequence_set_vibro_on);
        loader_port_delay_ms(50);
        notification_message(app->notification, &sequence_reset_vibro);
}
"""

class VerifyPatchTests(unittest.TestCase):
    def test_md5_verification_is_required_before_success(self):
        patched=patch_text(SOURCE)
        self.assertIn("err = esp_loader_flash_verify();",patched)
        self.assertIn("FLASH VERIFICATION FAILED",patched)
        self.assertIn("Flash MD5 verification PASSED.",patched)
        self.assertIn("#if MD5_ENABLED",patched)
        self.assertIn("#else",patched)
        self.assertIn("return ESP_LOADER_ERROR_FAIL;",patched)
        self.assertLess(patched.index("err = esp_loader_flash_verify();"),
                        patched.index("return ESP_LOADER_SUCCESS;"))

    def test_sd_read_failure_and_empty_images_fail_closed(self):
        patched=patch_text(SOURCE)
        self.assertIn("if(size == 0 || size > 0xFFFFFFFFu)",patched)
        self.assertIn("if(num_bytes != to_read)",patched)
        self.assertIn("Firmware SD read failed",patched)
        self.assertIn("storage_file_close(bin_file)",patched)
        self.assertIn("storage_file_free(bin_file)",patched)

    def test_no_unreviewed_or_duplicate_patch(self):
        with self.assertRaises(PatchMismatch):
            patch_text(SOURCE.replace("// TODO verify","// changed upstream"))
        with self.assertRaises(PatchMismatch):
            patch_text(SOURCE+"\n    // TODO verify")
        with self.assertRaises(PatchMismatch):
            patch_text(patch_text(SOURCE))

    def test_failure_blocks_success_banner_board_reset_and_success_buzz(self):
        patched=patch_text(SOURCE)
        self.assertIn("static bool _flash_all_files(EspFlasherApp* app)",patched)
        self.assertIn("Image write/MD5 failed; aborting remaining files.",patched)
        self.assertIn("const bool operation_ok = is_switch ? switched_ok : _flash_all_files(app);",patched)
        self.assertIn("if(operation_ok) {",patched)
        self.assertIn("FLASH VERIFIED.",patched)
        self.assertIn("FLASH FAILED / UNVERIFIED.",patched)
        self.assertNotIn("Done flashing. Please reset the board",patched)
        success=patched.split("if(operation_ok) {",1)[1].split("} else {",1)[0]
        failure=patched.split("} else {",1)[1]
        self.assertIn("loader_port_reset_target();",success)
        self.assertNotIn("loader_port_reset_target();",failure)
        self.assertNotIn("sequence_set_vibro_on",failure)

    def test_ota_firmware_switch_flags_are_both_verified(self):
        patched=patch_text(SOURCE)
        self.assertIn("static bool _switch_fw(EspFlasherApp* app, bool* switched_ok)",patched)
        self.assertIn("*switched_ok = false;",patched)
        self.assertIn("*switched_ok = true;",patched)
        self.assertIn("Firmware A flag MD5 FAILED.",patched)
        self.assertIn("Firmware B flag MD5 FAILED.",patched)
        self.assertIn("const bool is_switch = _switch_fw(app, &switched_ok);",patched)

    def test_no_blind_success_without_md5(self):
        modified=patch_text(SOURCE)
        self.assertIn('Flash MD5 verification unavailable: refusing success.',modified)
        self.assertIn('if(err != ESP_LOADER_SUCCESS)',modified)

if __name__=="__main__":unittest.main()
