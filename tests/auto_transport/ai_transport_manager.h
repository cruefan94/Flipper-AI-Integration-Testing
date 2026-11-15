#ifndef AI_TRANSPORT_MANAGER_H
#define AI_TRANSPORT_MANAGER_H
#include "ai_transport_policy.h"
typedef struct {AiTransport current,candidate;uint8_t candidate_observations;} AiTransportManager;
static inline AiTransport ai_transport_manager_update(AiTransportManager* m,AiTransportMode mode,const AiTransportAvailability* a) {
 if(!m||!a)return AI_TRANSPORT_NONE;
 AiTransport desired=ai_transport_select(mode,a);
 if(mode!=AI_TRANSPORT_MODE_AUTO){m->current=desired;m->candidate=AI_TRANSPORT_NONE;m->candidate_observations=0;return desired;}
 AiTransportAvailability current_only={0};
 switch(m->current){
 case AI_TRANSPORT_BLE:current_only.ble_ready=a->ble_ready;break;
 case AI_TRANSPORT_WIFI_STA:current_only.wifi_sta_ready=a->wifi_sta_ready;current_only.wifi_sta_authenticated=a->wifi_sta_authenticated;break;
 case AI_TRANSPORT_WIFI_AP:current_only.wifi_ap_ready=a->wifi_ap_ready;current_only.wifi_ap_authenticated=a->wifi_ap_authenticated;break;
 case AI_TRANSPORT_USB:current_only.usb_ready=a->usb_ready;current_only.usb_authenticated=a->usb_authenticated;break;
 default:break;
 }
 bool valid=m->current!=AI_TRANSPORT_NONE&&ai_transport_select(
 m->current==AI_TRANSPORT_BLE?AI_TRANSPORT_MODE_BLE:
 m->current==AI_TRANSPORT_WIFI_STA?AI_TRANSPORT_MODE_HOME_WIFI:
 m->current==AI_TRANSPORT_WIFI_AP?AI_TRANSPORT_MODE_PRIVATE_HOTSPOT:AI_TRANSPORT_MODE_USB,
 &current_only)==m->current;
 if(!valid||desired==m->current){if(!valid)m->current=desired;m->candidate=AI_TRANSPORT_NONE;m->candidate_observations=0;return m->current;}
 if(desired!=m->candidate){m->candidate=desired;m->candidate_observations=1;}
 else if(m->candidate_observations<3)m->candidate_observations++;
 if(m->candidate_observations>=3){m->current=desired;m->candidate=AI_TRANSPORT_NONE;m->candidate_observations=0;}
 return m->current;
}
#endif
