#include <assert.h>
#include "ai_transport_policy.h"
int main(void){AiTransportAvailability a={0};
assert(ai_transport_select(AI_TRANSPORT_MODE_AUTO,&a)==AI_TRANSPORT_NONE);
a.ble_ready=true;assert(ai_transport_select(AI_TRANSPORT_MODE_AUTO,&a)==AI_TRANSPORT_BLE);
a.wifi_sta_ready=true;assert(ai_transport_select(AI_TRANSPORT_MODE_AUTO,&a)==AI_TRANSPORT_BLE);
a.wifi_sta_authenticated=true;assert(ai_transport_select(AI_TRANSPORT_MODE_AUTO,&a)==AI_TRANSPORT_WIFI_STA);
a.wifi_ap_ready=true;a.wifi_ap_authenticated=true;assert(ai_transport_select(AI_TRANSPORT_MODE_PRIVATE_HOTSPOT,&a)==AI_TRANSPORT_WIFI_AP);
a.wifi_sta_authenticated=false;assert(ai_transport_select(AI_TRANSPORT_MODE_AUTO,&a)==AI_TRANSPORT_WIFI_AP);
a.wifi_ap_authenticated=false;assert(ai_transport_select(AI_TRANSPORT_MODE_AUTO,&a)==AI_TRANSPORT_BLE);
return 0;}
