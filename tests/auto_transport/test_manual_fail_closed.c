#include <assert.h>
#include "ai_transport_manager.h"

/* Regression: manual selection never chooses an alternate backend. */
int main(void) {
    AiTransportManager m = {0};
    AiTransportAvailability a = {0};
    a.ble_ready = true;
    assert(ai_transport_manager_update(&m, AI_TRANSPORT_MODE_HOME_WIFI, &a) == AI_TRANSPORT_NONE);
    assert(ai_transport_manager_update(&m, AI_TRANSPORT_MODE_PRIVATE_HOTSPOT, &a) == AI_TRANSPORT_NONE);
    assert(ai_transport_manager_update(&m, AI_TRANSPORT_MODE_USB, &a) == AI_TRANSPORT_NONE);
    assert(ai_transport_manager_update(&m, AI_TRANSPORT_MODE_BLE, &a) == AI_TRANSPORT_BLE);
    a.ble_ready = false;
    a.wifi_sta_ready = true;
    assert(ai_transport_manager_update(&m, AI_TRANSPORT_MODE_BLE, &a) == AI_TRANSPORT_NONE);
    assert(ai_transport_manager_update(&m, AI_TRANSPORT_MODE_AUTO, &a) == AI_TRANSPORT_NONE);
    a.wifi_sta_authenticated = true;
    assert(ai_transport_manager_update(&m, AI_TRANSPORT_MODE_HOME_WIFI, &a) == AI_TRANSPORT_WIFI_STA);
    return 0;
}
