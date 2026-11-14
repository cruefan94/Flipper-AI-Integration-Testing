/* Flipper AI ESP32 Manager — standalone, isolated UART companion FAP.
 * LPUART: Flipper pin 15 TX -> ESP32 RX2/GPIO16, pin 16 RX <- TX2/GPIO17, common GND.
 * ESP Flasher remains a separate upstream app; this app never writes flash.
 */
#include <furi.h>
#include <furi_hal.h>
#include <gui/gui.h>
#include <gui/view_dispatcher.h>
#include <gui/modules/submenu.h>
#include <gui/modules/text_box.h>
#include <storage/storage.h>
#include <string.h>
#include <stdlib.h>

enum { EspViewMenu, EspViewText };
enum {
    EspDetect, EspInfo, EspCaps, EspStatus, EspPassiveScan,
    EspLedOn, EspLedOff, EspFlashHelp,
    EspWatchBoards, EspInstallerHelp, EspBoardDevboard, EspBoardEsp32, EspBoardUnoR3,
    EspBoardUnoR4, EspReviewSdPlan, EspAbout
};
#define ESP_RX_LINE 192
#define ESP_SD_PLAN_PATH "/ext/apps_data/esp_flasher/flipper-ai-esp32-plan.txt"
#define ESP_SD_PLAN_LIMIT 1536

typedef struct {
    Gui* gui;
    ViewDispatcher* dispatcher;
    Submenu* submenu;
    TextBox* text_box;
    FuriHalSerialHandle* serial;
    FuriStreamBuffer* rx;
    FuriString* text;
    char line[ESP_RX_LINE];
    size_t used;
    bool discarding;
    bool waiting;
    uint16_t ticks;
    bool auto_watch;
    bool watch_probe_pending;
    uint16_t watch_ticks;
    uint16_t watch_probe_ticks;
} EspManager;

static uint32_t esp_previous_menu(void* context) {
    UNUSED(context);
    return EspViewMenu;
}
static uint32_t esp_previous_exit(void* context) {
    UNUSED(context);
    return VIEW_NONE;
}
static bool esp_navigation(void* context) {
    UNUSED(context);
    return false;
}
static void esp_show(EspManager* app, const char* text) {
    furi_string_set(app->text, text);
    text_box_set_text(app->text_box, furi_string_get_cstr(app->text));
    text_box_set_focus(app->text_box, TextBoxFocusStart);
    view_dispatcher_switch_to_view(app->dispatcher, EspViewText);
}
/* Only read a plan that the owner's host-side verified stager created.
 * Plan content is advisory; no ROM identity, publisher authentication or
 * permission to flash can be inferred from text on an SD card.
 */
static void esp_review_sd_plan(EspManager* app) {
    Storage* storage = furi_record_open(RECORD_STORAGE);
    File* file = storage_file_alloc(storage);
    if(!storage_file_open(file, ESP_SD_PLAN_PATH, FSAM_READ, FSOM_OPEN_EXISTING)) {
        esp_show(app, "NO STAGED FIRMWARE PLAN\n"
            "Use the verified host-side installer to stage a matched package:\n"
            "apps_data/esp_flasher/\n"
            "It never automatically flashes hardware.");
        storage_file_free(file);
        furi_record_close(RECORD_STORAGE);
        return;
    }
    uint64_t length = storage_file_size(file);
    char* data = NULL;
    if(length>0 && length<=ESP_SD_PLAN_LIMIT) data = malloc((size_t)length+1);
    size_t got=0;
    if(data) {
        while(got < (size_t)length) {
            size_t n = storage_file_read(file, data+got, (size_t)length-got);
            if(!n) break;
            got += n;
        }
    }
    storage_file_close(file);
    storage_file_free(file);
    furi_record_close(RECORD_STORAGE);
    if(!data || got!=(size_t)length) {
        free(data);
        esp_show(app, "INVALID OR INCOMPLETE SD FIRMWARE PLAN\n"
            "No update offered. Re-stage a checked package.");
        return;
    }
    data[got]=0;
    bool clean=true;
    for(size_t i=0;i<got;i++) {
        unsigned char ch=(unsigned char)data[i];
        if(ch==0 || (ch<32 && ch!='\n') || ch>126) {
            clean=false;
            break;
        }
    }
    const char* classic = "FZHW1|BOARD=esp32_wroom32_devkit|CHIP=esp32|";
    const char* devboard = "FZHW1|BOARD=flipper_wifi_devboard_s2|CHIP=esp32s2|";
    bool matching_family =
        strncmp(data,classic,strlen(classic))==0 ||
        strncmp(data,devboard,strlen(devboard))==0;
    if(!clean || !matching_family ||
       !strstr(data, "|HW_UNVERIFIED=1\n") ||
       !strstr(data, "NOTICE|SD_COPY_ONLY|ESP_FLASHER_APPROVAL_REQUIRED\n")) {
        free(data);
        esp_show(app, "UNSUPPORTED SD FIRMWARE PLAN\n"
            "Wrong family, invalid characters or absent approval warning.\n"
            "Do not flash. Re-stage an approved image.");
        return;
    }
    furi_string_set(app->text,
        "STAGED FIRMWARE - REVIEW ONLY\n"
        "SD text is NOT chip ID or approved firmware.\n"
        "Verify chip, actual flash capacity, GPIO and image offsets.\n"
        "Owner approval in ESP Flasher is required.\n\n");
    furi_string_cat_str(app->text,data);
    text_box_set_text(app->text_box,furi_string_get_cstr(app->text));
    text_box_set_focus(app->text_box,TextBoxFocusStart);
    view_dispatcher_switch_to_view(app->dispatcher,EspViewText);
    free(data);
}

static void esp_send(EspManager* app, const char* command) {
    if(!app->serial) {
        esp_show(app, "LPUART busy or unavailable.\nExit Flipper AI and other UART apps first.");
        return;
    }
    /* A manual command supersedes an in-flight background read-only probe. */
    app->watch_probe_pending = false;
    app->watch_probe_ticks = 0;
    app->waiting = true;
    app->ticks = 0;
    app->used = 0;
    app->discarding = false;
    furi_stream_buffer_reset(app->rx);
    esp_show(app, "Waiting for ESP32...\n");
    furi_hal_serial_tx(app->serial, (const uint8_t*)command, strlen(command));
    furi_hal_serial_tx(app->serial, (const uint8_t*)"\n", 1);
}
static void esp_line(EspManager* app, const char* line) {
    if(app->watch_probe_pending && !app->waiting && strncmp(line, "FZ1|OK|CHIP=", 12) == 0) {
        app->watch_probe_pending = false;
        /* FZ1 protocol replies are hints from an already installed companion,
         * not authenticated ESP ROM chip IDs. Never auto-select a flash image. */
        if(strncmp(line + 12, "ESP32,", 6) == 0) {
            esp_show(app, "HARDWARE FOUND (FZ1 RESPONSE)\n"
                "ESP32-classic companion detected on UART2.\n"
                "Profile: ESP-WROOM-32 / ESP32 DevKit.\n"
                "Already running Flipper AI companion firmware.\n"
                "Installer can offer a verified ESP32-only firmware candidate.\n"
                "FLASHING REQUIRES APPROVAL and ESP Flasher.\n"
                "No firmware has been changed.");
        } else if(strncmp(line + 12, "ESP32-S2,", 9) == 0) {
            esp_show(app, "HARDWARE FOUND (FZ1 RESPONSE)\n"
                "ESP32-S2 companion replied.\n"
                "Do not infer official Wi-Fi Devboard identity.\n"
                "Keep stock debug/Black Magic firmware unless deliberately switching.\n"
                "Only an approved ESP32-S2 package may be used.");
        } else {
            esp_show(app, "Companion replied but chip is not in the approved installer profiles.\n"
                "No firmware target selected; no flash initiated.");
        }
        return;
    }
    if(!app->waiting || strncmp(line, "FZ1|", 4) != 0) return;
    if(strcmp(line, "FZ1|END") == 0) {
        app->waiting = false;
        return;
    }
    const char* info = NULL;
    if(strncmp(line, "FZ1|OK|", 7) == 0) info = line + 7;
    if(strncmp(line, "FZ1|DATA|", 9) == 0) info = line + 9;
    if(strncmp(line, "FZ1|ERR|", 8) == 0) info = line + 4;
    if(info && furi_string_size(app->text) < 1800) {
        furi_string_cat_str(app->text, info);
        furi_string_cat_str(app->text, "\n");
        text_box_set_text(app->text_box, furi_string_get_cstr(app->text));
    }
}
static void esp_rx_isr(FuriHalSerialHandle* serial, FuriHalSerialRxEvent event, void* context) {
    EspManager* app = context;
    if(event == FuriHalSerialRxEventData) {
        const uint8_t b = furi_hal_serial_async_rx(serial);
        furi_stream_buffer_send(app->rx, &b, 1, 0);
    }
}
static void esp_tick(void* context) {
    EspManager* app = context;
    uint8_t b;
    uint16_t budget = 256;
    while(budget-- && furi_stream_buffer_receive(app->rx, &b, 1, 0) == 1) {
        if(b == '\n') {
            if(!app->discarding) {
                app->line[app->used] = 0;
                esp_line(app, app->line);
            }
            app->used = 0;
            app->discarding = false;
        } else if(b != '\r' && !app->discarding) {
            if(app->used < ESP_RX_LINE - 1) app->line[app->used++] = (char)b;
            else { app->used = 0; app->discarding = true; }
        }
    }
    if(app->auto_watch && app->serial && !app->waiting) {
        /* Monitoring is opt-in. UART has no reliable physical hot-plug signal.
         * Never probe other UART owners or send programming/reset commands. */
        if(app->watch_probe_pending) {
            if(++app->watch_probe_ticks > 25) app->watch_probe_pending = false;
        } else if(++app->watch_ticks > 50) {
            const char* probe = "FZ1|INFO\n";
            furi_hal_serial_tx(app->serial, (const uint8_t*)probe, strlen(probe));
            app->watch_probe_pending = true;
            app->watch_probe_ticks = 0;
            app->watch_ticks = 0;
        }
    }
    if(app->waiting && ++app->ticks > 200) {
        app->waiting = false;
        furi_string_cat_str(app->text, "Timed out.\nCheck wiring, power and firmware.\n");
        text_box_set_text(app->text_box, furi_string_get_cstr(app->text));
    }
}
static void esp_menu(void* context, uint32_t index) {
    EspManager* app = context;
    switch(index) {
    case EspDetect: esp_send(app, "FZ1|PING"); break;
    case EspInfo: esp_send(app, "FZ1|INFO"); break;
    case EspCaps: esp_send(app, "FZ1|CAPS"); break;
    case EspStatus: esp_send(app, "FZ1|STATUS"); break;
    case EspPassiveScan: esp_send(app, "FZ1|WIFI_SCAN"); break;
    case EspLedOn: esp_send(app, "FZ1|LED|ON"); break;
    case EspLedOff: esp_send(app, "FZ1|LED|OFF"); break;
    case EspWatchBoards:
        app->auto_watch = !app->auto_watch;
        app->watch_ticks = 0;
        app->watch_probe_ticks = 0;
        app->watch_probe_pending = false;
        esp_show(app, app->auto_watch
            ? "AUTO-DETECT IS ON (APP MUST STAY OPEN)\n"
              "Checks for an installed FZ1 companion on UART2 every ~5 seconds.\n"
              "A blank board or an Arduino Uno cannot be safely identified this way.\n"
              "Detection offers a match; it NEVER flashes automatically.\n"
              "Use Hardware installer guide for wiring and approved updates."
            : "AUTO-DETECT IS OFF.\n"
              "No background polling or automatic flashing.\n"
              "Existing firmware and hardware are unchanged.");
        break;
    case EspReviewSdPlan:
        esp_review_sd_plan(app);
        break;
    case EspInstallerHelp:
        esp_show(app, "HARDWARE INSTALLER - PREFLIGHT\n"
            "1. Detect board (if running FZ1) or select exact model.\n"
            "2. Verify 3.3V UART or isolate 5V Uno with level shifting.\n"
            "3. Match chip, flash layout, signed/trusted source + SHA256.\n"
            "4. Preview actions; approve EVERY firmware flash.\n"
            "5. Use compatible Flipper ESP Flasher or external supported host.\n"
            "6. Read back/verify and keep recovery/backup.\n"
            "This Manager does not run ESP Flasher or flash other boards.");
        break;
    case EspBoardDevboard:
        esp_show(app, "OFFICIAL FLIPPER WI-FI DEVBOARD\n"
            "ESP32-S2-WROVER (not ESP32 classic).\n"
            "Default Black Magic/debug firmware must be preserved unless you approve a change.\n"
            "Official host update: ufbt devboard_flash with board in BOOT mode.\n"
            "Flipper ESP Flasher may support S2 with board-specific verified images.\n"
            "Never load an ESP32-WROOM-32 image onto this board.");
        break;
    case EspBoardEsp32:
        esp_show(app, "ESP-WROOM-32 DEVKIT / 38-PIN\n"
            "Prototype board profile: classic ESP32; exact flash size not verified.\n"
            "Manager: UART2 RX GPIO16 / TX GPIO17, Flipper 15/16 and common GND.\n"
            "Flashing: separate UART0, Flipper USART pins 13/14, manual BOOT/EN.\n"
            "Use an ESP32 matched/verified bundle with ESP Flasher.\n"
            "Do not connect ESP USB-UART and Flipper TX drivers in conflict.");
        break;
    case EspBoardUnoR3:
        esp_show(app, "ARDUINO UNO R3-STYLE\n"
            "ATmega328P family, 5V digital I/O.\n"
            "DO NOT CONNECT 5V UART DIRECTLY TO FLIPPER GPIO.\n"
            "Preferred first updater: Raspberry Pi / PC with USB + avrdude.\n"
            "USB bootloader/programmer must be verified; clones vary.\n"
            "Flipper-only Uno programmer needs separate 3.3V/5V level shifting\n"
            "and an authored/verified AVR ISP backend. Not available yet.");
        break;
    case EspBoardUnoR4:
        esp_show(app, "ARDUINO UNO R4 (MINIMA / WIFI)\n"
            "Renesas RA4M1; NOT the Uno R3 ATmega328P.\n"
            "R3 .hex and AVR upload tools are not valid for this board.\n"
            "Use the correct Arduino board package via USB host.\n"
            "No Flipper-side automatic programmer is implemented.");
        break;
    case EspFlashHelp:
        esp_show(app,
            "FLASHING IS SEPARATE.\n"
            "Use compatible ESP Flasher from Apps > GPIO.\n"
            "Verify board model and matching .bin first.\n"
            "Program: FZ 13 TX -> ESP RX0.\n"
            "FZ 14 RX <- ESP TX0.\n"
            "Use manual BOOT/EN as instructed.\n"
            "For Manager use FZ 15/16 RX2/TX2.\n"
            "Never flash guessed images.");
        break;
    case EspAbout:
        esp_show(app,
            "ESP32 Manager v0.1 SOURCE PROTOTYPE\n"
            "FZ1 115200 8N1 LPUART.\n"
            "Manager: FZ 15 TX -> ESP RX2 GPIO16\n"
            "Manager: FZ 16 RX <- ESP TX2 GPIO17\n"
            "Common GND; ESP separately powered.\n"
            "Not yet Momentum/device verified.");
        break;
    }
}
int32_t esp_manager_app(void* p) {
    UNUSED(p);
    EspManager* app = calloc(1, sizeof(EspManager));
    if(!app) return 255;
    app->text = furi_string_alloc();
    app->rx = furi_stream_buffer_alloc(512, 1);
    app->gui = furi_record_open(RECORD_GUI);
    app->dispatcher = view_dispatcher_alloc();
    app->submenu = submenu_alloc();
    app->text_box = text_box_alloc();
    text_box_set_font(app->text_box, TextBoxFontText);
    view_dispatcher_set_event_callback_context(app->dispatcher, app);
    view_dispatcher_set_navigation_event_callback(app->dispatcher, esp_navigation);
    view_dispatcher_set_tick_event_callback(app->dispatcher, esp_tick, 100);
    submenu_add_item(app->submenu, "Detect ESP32", EspDetect, esp_menu, app);
    submenu_add_item(app->submenu, "Board info", EspInfo, esp_menu, app);
    submenu_add_item(app->submenu, "Capabilities", EspCaps, esp_menu, app);
    submenu_add_item(app->submenu, "Diagnostics", EspStatus, esp_menu, app);
    submenu_add_item(app->submenu, "Passive Wi-Fi scan", EspPassiveScan, esp_menu, app);
    submenu_add_item(app->submenu, "LED on (optional)", EspLedOn, esp_menu, app);
    submenu_add_item(app->submenu, "LED off (optional)", EspLedOff, esp_menu, app);
    submenu_add_item(app->submenu, "Hardware installer guide", EspInstallerHelp, esp_menu, app);
    submenu_add_item(app->submenu, "Review staged SD firmware", EspReviewSdPlan, esp_menu, app);
    submenu_add_item(app->submenu, "Auto-detect attached (toggle)", EspWatchBoards, esp_menu, app);
    submenu_add_item(app->submenu, "Profile: Wi-Fi Devboard S2", EspBoardDevboard, esp_menu, app);
    submenu_add_item(app->submenu, "Profile: ESP32-WROOM", EspBoardEsp32, esp_menu, app);
    submenu_add_item(app->submenu, "Profile: Arduino Uno R3", EspBoardUnoR3, esp_menu, app);
    submenu_add_item(app->submenu, "Profile: Arduino Uno R4", EspBoardUnoR4, esp_menu, app);
    submenu_add_item(app->submenu, "How to flash firmware", EspFlashHelp, esp_menu, app);
    submenu_add_item(app->submenu, "About", EspAbout, esp_menu, app);
    view_set_previous_callback(submenu_get_view(app->submenu), esp_previous_exit);
    view_set_previous_callback(text_box_get_view(app->text_box), esp_previous_menu);
    view_dispatcher_add_view(app->dispatcher, EspViewMenu, submenu_get_view(app->submenu));
    view_dispatcher_add_view(app->dispatcher, EspViewText, text_box_get_view(app->text_box));
    view_dispatcher_attach_to_gui(app->dispatcher, app->gui, ViewDispatcherTypeFullscreen);
    app->serial = furi_hal_serial_control_acquire(FuriHalSerialIdLpuart);
    if(app->serial) {
        furi_hal_serial_init(app->serial, 115200);
        furi_hal_serial_async_rx_start(app->serial, esp_rx_isr, app, false);
    }
    view_dispatcher_switch_to_view(app->dispatcher, EspViewMenu);
    view_dispatcher_run(app->dispatcher);
    if(app->serial) {
        furi_hal_serial_async_rx_stop(app->serial);
        furi_hal_serial_deinit(app->serial);
        furi_hal_serial_control_release(app->serial);
    }
    view_dispatcher_remove_view(app->dispatcher, EspViewMenu);
    view_dispatcher_remove_view(app->dispatcher, EspViewText);
    text_box_free(app->text_box);
    submenu_free(app->submenu);
    view_dispatcher_free(app->dispatcher);
    furi_record_close(RECORD_GUI);
    furi_stream_buffer_free(app->rx);
    furi_string_free(app->text);
    free(app);
    return 0;
}
