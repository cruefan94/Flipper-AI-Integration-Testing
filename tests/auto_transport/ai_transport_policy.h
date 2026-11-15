#ifndef AI_TRANSPORT_POLICY_H
#define AI_TRANSPORT_POLICY_H
#include <stdbool.h>
#include <stdint.h>
typedef enum {AI_TRANSPORT_NONE=0,AI_TRANSPORT_BLE,AI_TRANSPORT_WIFI_STA,AI_TRANSPORT_WIFI_AP,AI_TRANSPORT_USB} AiTransport;
typedef enum {AI_TRANSPORT_MODE_AUTO=0,AI_TRANSPORT_MODE_BLE,AI_TRANSPORT_MODE_HOME_WIFI,AI_TRANSPORT_MODE_PRIVATE_HOTSPOT,AI_TRANSPORT_MODE_USB} AiTransportMode;
typedef struct {bool ble_ready,wifi_sta_ready,wifi_ap_ready,usb_ready,wifi_sta_authenticated,wifi_ap_authenticated,usb_authenticated;} AiTransportAvailability;
static inline AiTransport ai_transport_select(AiTransportMode mode,const AiTransportAvailability* a) {
 if(!a) return AI_TRANSPORT_NONE;
 bool sta=a->wifi_sta_ready&&a->wifi_sta_authenticated,ap=a->wifi_ap_ready&&a->wifi_ap_authenticated,usb=a->usb_ready&&a->usb_authenticated;
 switch(mode) {
 case AI_TRANSPORT_MODE_BLE:return a->ble_ready?AI_TRANSPORT_BLE:AI_TRANSPORT_NONE;
 case AI_TRANSPORT_MODE_HOME_WIFI:return sta?AI_TRANSPORT_WIFI_STA:AI_TRANSPORT_NONE;
 case AI_TRANSPORT_MODE_PRIVATE_HOTSPOT:return ap?AI_TRANSPORT_WIFI_AP:AI_TRANSPORT_NONE;
 case AI_TRANSPORT_MODE_USB:return usb?AI_TRANSPORT_USB:AI_TRANSPORT_NONE;
 case AI_TRANSPORT_MODE_AUTO:if(sta)return AI_TRANSPORT_WIFI_STA;if(ap)return AI_TRANSPORT_WIFI_AP;if(a->ble_ready)return AI_TRANSPORT_BLE;return usb?AI_TRANSPORT_USB:AI_TRANSPORT_NONE;
 default:return AI_TRANSPORT_NONE;
 }
}
#endif
