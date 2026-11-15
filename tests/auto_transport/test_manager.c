#include <assert.h>
#include "ai_transport_manager.h"
int main(void){AiTransportManager m={0};AiTransportAvailability a={0};
assert(ai_transport_manager_update(&m,AI_TRANSPORT_MODE_AUTO,&a)==AI_TRANSPORT_NONE);
a.ble_ready=true;assert(ai_transport_manager_update(&m,AI_TRANSPORT_MODE_AUTO,&a)==AI_TRANSPORT_BLE);
a.wifi_sta_ready=true;a.wifi_sta_authenticated=true;
assert(ai_transport_manager_update(&m,AI_TRANSPORT_MODE_AUTO,&a)==AI_TRANSPORT_BLE);
assert(ai_transport_manager_update(&m,AI_TRANSPORT_MODE_AUTO,&a)==AI_TRANSPORT_BLE);
assert(ai_transport_manager_update(&m,AI_TRANSPORT_MODE_AUTO,&a)==AI_TRANSPORT_WIFI_STA);
a.wifi_sta_authenticated=false;assert(ai_transport_manager_update(&m,AI_TRANSPORT_MODE_AUTO,&a)==AI_TRANSPORT_BLE);
return 0;}
