#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reviewable patch for upstream GPL-3.0 ESP Flasher, pinned at 1f6f801c.
Compile upstream+patch, never pretend a successful write proves flash integrity.

Upstream: https://github.com/0xchocolate/flipperzero-esp-flasher
Library: Espressif esp-serial-flasher MD5_ENABLED esp_loader_flash_verify().
Does not flash, run a serial programmer or alter hardware by itself.
"""
from pathlib import Path
import argparse
import sys

UPSTREAM_SHA="1f6f801c3ebecbc4afbf6500564bf99748710e24"

class PatchMismatch(RuntimeError):
    pass

def once(source,from_text,to_text):
    if source.count(from_text)!=1:raise PatchMismatch(
        "Upstream ESP Flasher changed; refusing unreviewed blind patch")
    return source.replace(from_text,to_text,1)

def patch_text(source):
    if "Flipper AI: checked flash MD5" in source:
        raise PatchMismatch("Already patched")
    source=once(source,
      "    uint64_t size = storage_file_size(bin_file);",
      """    uint64_t size = storage_file_size(bin_file);
    if(size == 0 || size > 0xFFFFFFFFu) {
        loader_port_debug_print("Refusing an empty or too-large flash image.\\n");
        storage_file_close(bin_file);
        storage_file_free(bin_file);
        return ESP_LOADER_ERROR_FAIL;
    }""")
    source=once(source,
      "        uint16_t num_bytes = storage_file_read(bin_file, payload, to_read);",
      """        uint16_t num_bytes = storage_file_read(bin_file, payload, to_read);
        /* A short/empty SD read must never be mistaken for a completed write.
         * The original loop could retry an empty read indefinitely. */
        if(num_bytes != to_read) {
            loader_port_debug_print("Firmware SD read failed or was incomplete.\\n");
            storage_file_close(bin_file);
            storage_file_free(bin_file);
            return ESP_LOADER_ERROR_FAIL;
        }""")
    source=once(source,
      "    // TODO verify",
      """    /* Flipper AI: checked flash MD5 against the bytes sent to the chip.
     * This is not a cryptographic publisher signature or a hardware test.
     * Fail closed if a target does not implement flash MD5 verification. */
#if MD5_ENABLED
    loader_port_debug_print("Verifying programmed flash MD5...\\n");
    err = esp_loader_flash_verify();
    if(err != ESP_LOADER_SUCCESS) {
        snprintf(user_msg, sizeof(user_msg),
                 "FLASH VERIFICATION FAILED: %d\\n", err);
        loader_port_debug_print(user_msg);
        storage_file_close(bin_file);
        storage_file_free(bin_file);
        return err;
    }
    loader_port_debug_print("Flash MD5 verification PASSED.\\n");
#else
    loader_port_debug_print("Flash MD5 verification unavailable: refusing success.\\n");
    storage_file_close(bin_file);
    storage_file_free(bin_file);
    return ESP_LOADER_ERROR_FAIL;
#endif""")
    # An MD5 error printed by _flash_file must propagate through the worker.
    # Upstream _flash_all_files is void and always leaves the outer caller
    # showing "Done flashing" (and resetting the ESP), even after a failed write.
    source=once(source,
      "static void _flash_all_files(EspFlasherApp* app) {",
      "static bool _flash_all_files(EspFlasherApp* app) {")
    source=once(source,
      "    int current_step = 1;",
      """    if(num_steps <= 0) {
        loader_port_debug_print("No firmware images selected: refusing flash.\\n");
        return false;
    }
    int current_step = 1;""")
    source=once(source,
      """            if(err) {
                break;
            }""",
      """            if(err != ESP_LOADER_SUCCESS) {
                loader_port_debug_print("Image write/MD5 failed; aborting remaining files.\\n");
                return false;
            }""")
    source=once(source,
      """    }
}

static int32_t esp_flasher_flash_bin(void* context) {""",
      """    }
    return true;
}

static int32_t esp_flasher_flash_bin(void* context) {""")

    # OTA selector also writes two small blocks. Preserve its existing option
    # but report success ONLY after the chip confirms MD5 on both blocks.
    source=once(source,
      "static bool _switch_fw(EspFlasherApp* app) {",
      """static bool _switch_fw(EspFlasherApp* app, bool* switched_ok) {
    *switched_ok = false;""")
    source=once(source,
      '    loader_port_debug_print("Preparing to set flags for firmware B\\n");',
      """#if MD5_ENABLED
    err = esp_loader_flash_verify();
    if(err != ESP_LOADER_SUCCESS) {
        loader_port_debug_print("Firmware A flag MD5 FAILED.\\n");
        return true;
    }
#else
    loader_port_debug_print("MD5 unavailable for firmware flags.\\n");
    return true;
#endif
    loader_port_debug_print("Preparing to set flags for firmware B\\n");""")
    source=once(source,
      """    loader_port_debug_print("Finished programming\\n");
    return true;
}""",
      """#if MD5_ENABLED
    err = esp_loader_flash_verify();
    if(err != ESP_LOADER_SUCCESS) {
        loader_port_debug_print("Firmware B flag MD5 FAILED.\\n");
        return true;
    }
#else
    loader_port_debug_print("MD5 unavailable for firmware flags.\\n");
    return true;
#endif
    *switched_ok = true;
    loader_port_debug_print("Firmware flags programmed and MD5 verified.\\n");
    return true;
}""")

    source=once(source,
      """        if(!_switch_fw(app)) {
            _flash_all_files(app);
        }
        app->switch_fw = SwitchNotSet;""",
      """        bool switched_ok = false;
        const bool is_switch = _switch_fw(app, &switched_ok);
        const bool operation_ok = is_switch ? switched_ok : _flash_all_files(app);
        app->switch_fw = SwitchNotSet;""")
    source=once(source,
      """        loader_port_debug_print(
            "Done flashing. Please reset the board manually if it doesn't auto-reset.\\n");

        // auto-reset for supported boards
        loader_port_reset_target();

        // short buzz to alert user
        notification_message(app->notification, &sequence_set_vibro_on);
        loader_port_delay_ms(50);
        notification_message(app->notification, &sequence_reset_vibro);""",
      """        if(operation_ok) {
            loader_port_debug_print(
                "FLASH VERIFIED. Reset board if it doesn't auto-reset.\\n");
            // Only successful, verified operations may trigger reset/success buzz.
            loader_port_reset_target();
            notification_message(app->notification, &sequence_set_vibro_on);
            loader_port_delay_ms(50);
            notification_message(app->notification, &sequence_reset_vibro);
        } else {
            loader_port_debug_print(
                "FLASH FAILED / UNVERIFIED. No automatic reset. Check logs and recovery.\\n");
        }""")
    return source



def patch_target_checks(source):
    """Verify ROM chip identity and actual SPI flash size BEFORE any erase."""
    source=once(source,
      "static esp_loader_error_t _flash_file(EspFlasherApp* app, char* filepath, uint32_t addr) {",
      "static esp_loader_error_t _flash_file(EspFlasherApp* app, char* filepath, uint32_t addr, uint32_t capacity) {")
    source=once(source,
      '    loader_port_debug_print("Erasing flash...this may take a while\\n");',
      """    /* Reject writes beyond the flash capacity reported by the target ROM.
     * Never rely solely on the staged firmware image's text manifest. */
    if(capacity == 0 || addr >= capacity || size > (uint64_t)(capacity - addr)) {
        loader_port_debug_print("Firmware offset/size exceeds detected ESP flash. ABORT.\\n");
        storage_file_close(bin_file);
        storage_file_free(bin_file);
        return ESP_LOADER_ERROR_IMAGE_SIZE;
    }
    loader_port_debug_print("Erasing flash...this may take a while\\n");""")
    source=once(source,
      "static bool _flash_all_files(EspFlasherApp* app) {",
      "static bool _flash_all_files(EspFlasherApp* app, uint32_t capacity) {")
    source=once(source,
      "            err = _flash_file(app, item->path, item->addr);",
      "            err = _flash_file(app, item->path, item->addr, capacity);")
    source=once(source,
      """        const bool operation_ok = is_switch ? switched_ok : _flash_all_files(app);""",
      """        const bool operation_ok = is_switch ? switched_ok : _flash_all_files(app, actual_flash_size);""")
    source=once(source,
      """    err = esp_loader_connect(&connect_config);
    if(err != ESP_LOADER_SUCCESS) {""",
      """    err = esp_loader_connect(&connect_config);
    uint32_t actual_flash_size = 0;
    if(err == ESP_LOADER_SUCCESS) {
        const target_chip_t rom_chip = esp_loader_get_target();
        bool chip_ok = false;
        if(app->selected_flash_options[SelectedFlashC5Mode]) {
            chip_ok = rom_chip == ESP32C5_CHIP;
        } else if(app->selected_flash_options[SelectedFlashS3Mode]) {
            chip_ok = (rom_chip == ESP32S3_CHIP || rom_chip == ESP32C3_CHIP ||
                       rom_chip == ESP32C6_CHIP);
        } else {
            /* Safe default for the owner's 38-pin ESP-WROOM-32 classic.
             * S2 needs its own explicit chip-mode+flash-layout review. */
            chip_ok = rom_chip == ESP32_CHIP;
        }
        if(!chip_ok) {
            loader_port_debug_print("ESP ROM chip differs from selected board mode. NO FLASH.\\n");
            err = ESP_LOADER_ERROR_INVALID_TARGET;
        } else {
            esp_loader_error_t size_status = esp_loader_flash_detect_size(&actual_flash_size);
            if(size_status != ESP_LOADER_SUCCESS || actual_flash_size < 0x20000u) {
                loader_port_debug_print("ESP flash size unavailable/invalid. NO FLASH.\\n");
                err = ESP_LOADER_ERROR_IMAGE_SIZE;
            } else {
                char rom_report[112];
                snprintf(rom_report, sizeof(rom_report),
                         "ESP ROM chip=%u, flash capacity=%lu bytes.\\n",
                         (unsigned)rom_chip, (unsigned long)actual_flash_size);
                loader_port_debug_print(rom_report);
            }
        }
    }
    if(err != ESP_LOADER_SUCCESS) {""")
    return source


def patch_flasher_worker(source):
    return patch_target_checks(patch_text(source))


def patch_flash_confirmation(source):
    """Require a separate, positive on-device YES before writing image bytes."""
    return once(source,
      """        if(app->num_selected_flash_options) {
            // only start next scene if at least one option is selected
            scene_manager_next_scene(app->scene_manager, EspFlasherSceneConsoleOutput);
        }""",
      """        if(app->num_selected_flash_options) {
            /* A browse-menu selection is not yet approval to overwrite flash. */
            DialogMessage* confirm = dialog_message_alloc();
            dialog_message_set_header(
                confirm, "CONFIRM ESP FLASH", 64, 0, AlignCenter, AlignTop);
            dialog_message_set_text(
                confirm,
                "Check chip + offsets\\nExternal USB power\\nOverwrite flash now?",
                64, 15, AlignCenter, AlignTop);
            dialog_message_set_buttons(confirm, "Cancel", NULL, "FLASH");
            DialogMessageButton choice = dialog_message_show(app->dialogs, confirm);
            dialog_message_free(confirm);
            if(choice == DialogMessageButtonRight) {
                scene_manager_next_scene(app->scene_manager, EspFlasherSceneConsoleOutput);
            }
        }""")


def patch_switch_confirmation(source):
    """OTA slot writes also need affirmative consent, not just a menu click."""
    source=once(source,
      "void esp_flasher_scene_start_on_enter(void* context) {",
      """static bool flipper_ai_confirm_ota_write(EspFlasherApp* app, const char* question) {
    DialogMessage* confirm = dialog_message_alloc();
    dialog_message_set_header(
        confirm, "CONFIRM OTA WRITE", 64, 0, AlignCenter, AlignTop);
    dialog_message_set_text(confirm, question, 64, 15, AlignCenter, AlignTop);
    dialog_message_set_buttons(confirm, "Cancel", NULL, "WRITE");
    DialogMessageButton choice = dialog_message_show(app->dialogs, confirm);
    dialog_message_free(confirm);
    return choice == DialogMessageButtonRight;
}

void esp_flasher_scene_start_on_enter(void* context) {""")
    source=once(source,
      """        } else if(event.event == SubmenuIndexEspFlasherSwitchA) {
            app->switch_fw = SwitchToFirmwareA;
            scene_manager_next_scene(app->scene_manager, EspFlasherSceneConsoleOutput);
            consumed = true;""",
      """        } else if(event.event == SubmenuIndexEspFlasherSwitchA) {
            if(flipper_ai_confirm_ota_write(app, "Write A\\nOTA boot flags?")) {
                app->switch_fw = SwitchToFirmwareA;
                scene_manager_next_scene(app->scene_manager, EspFlasherSceneConsoleOutput);
            }
            consumed = true;""")
    source=once(source,
      """        } else if(event.event == SubmenuIndexEspFlasherSwitchB) {
            app->switch_fw = SwitchToFirmwareB;
            scene_manager_next_scene(app->scene_manager, EspFlasherSceneConsoleOutput);
            consumed = true;""",
      """        } else if(event.event == SubmenuIndexEspFlasherSwitchB) {
            if(flipper_ai_confirm_ota_write(app, "Write B\\nOTA boot flags?")) {
                app->switch_fw = SwitchToFirmwareB;
                scene_manager_next_scene(app->scene_manager, EspFlasherSceneConsoleOutput);
            }
            consumed = true;""")
    return source


def patch_power_policy(source):
    """External USB ESP32: do not auto-enable potentially conflicting 5 V OTG."""
    source=once(source,
      """    uint8_t attempts = 0;
    bool otg_was_enabled = furi_hal_power_is_otg_enabled();
    while(!furi_hal_power_is_otg_enabled() && attempts++ < 5) {
        furi_hal_power_enable_otg();
        furi_delay_ms(10);
    }
    furi_delay_ms(200);""",
      """    /* Flipper AI: ESP32 initially uses external USB power, shared GND and
     * 3.3 V UART. Opening the programmer never changes Flipper OTG power.
     * Confirm the onboard USB-UART bridge is not electrically contending. */""")
    source=once(source,
      """    if(furi_hal_power_is_otg_enabled() && !otg_was_enabled) {
        furi_hal_power_disable_otg();
    }""",
      """    /* No Flipper OTG power state changes were made by this app. */""")
    return source


def main():
    parser=argparse.ArgumentParser(description="GPL ESP Flasher MD5 verification patch only")
    parser.add_argument("checkout",type=Path)
    args=parser.parse_args()
    root=args.checkout.resolve()
    if not (root/"LICENSE").is_file() or not (root/"application.fam").is_file():
        parser.exit(2,"Refusing unknown ESP Flasher checkout\n")
    import subprocess
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                 text=True).strip()
    if sha!=UPSTREAM_SHA:
        parser.exit(2,"Unexpected upstream revision: refusing patch\n")
    transforms={
        "esp_flasher_worker.c":patch_flasher_worker,
        "scenes/esp_flasher_scene_browse.c":patch_flash_confirmation,
        "scenes/esp_flasher_scene_start.c":patch_switch_confirmation,
        "esp_flasher_app.c":patch_power_policy,
    }
    changes={}
    try:
        for relative,transform in transforms.items():
            path=root/relative
            if path.is_symlink() or not path.is_file():
                raise PatchMismatch("Missing or symlinked source: "+relative)
            changes[path]=transform(path.read_text())
    except PatchMismatch as exc:
        parser.exit(2,str(exc)+"\n")
    # Compute every exact-anchor source transform before writing any file.
    for path,patched in changes.items():
        path.write_text(patched)
    print("Applied pinned GPL ESP Flasher MD5 + confirmation + safe-power patch:",sha)

if __name__=="__main__":main()
