/* Flipper AI ESP32 Manager — standalone, isolated UART companion FAP.
 * LPUART: Flipper pin 15 TX -> classic ESP32 RX0, pin 16 RX <- TX0, common GND.
 * ESP Flasher remains a separate upstream app; this app never writes flash.
 */
#include <furi.h>
#include <furi_hal.h>
#include <gui/gui.h>
#include <gui/view_dispatcher.h>
#include <gui/modules/submenu.h>
#include <gui/modules/text_box.h>
#include <string.h>
#include <stdlib.h>

enum { EspViewMenu, EspViewText };
enum {
    EspDetect, EspInfo, EspCaps, EspStatus, EspPassiveScan,
    EspLedOn, EspLedOff, EspFlashHelp, EspAbout
};
#define ESP_RX_LINE 192

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
static void esp_send(EspManager* app, const char* command) {
    if(!app->serial) {
        esp_show(app, "LPUART busy or unavailable.\nExit Flipper AI and other UART apps first.");
        return;
    }
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
    case EspFlashHelp:
        esp_show(app,
            "FLASHING IS SEPARATE.\n"
            "Use compatible ESP Flasher from Apps > GPIO.\n"
            "Verify board model and matching .bin first.\n"
            "Use UART0 plus manual BOOT/EN as instructed.\n"
            "Never flash guessed images.");
        break;
    case EspAbout:
        esp_show(app,
            "ESP32 Manager v0.1 SOURCE PROTOTYPE\n"
            "FZ1 115200 8N1 LPUART.\n"
            "Flipper 15 TX -> ESP RX0\n"
            "Flipper 16 RX <- ESP TX0\n"
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
