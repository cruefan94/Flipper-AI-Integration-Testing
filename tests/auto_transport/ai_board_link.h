#ifndef AI_BOARD_LINK_H
#define AI_BOARD_LINK_H
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
typedef enum {AI_BOARD_UNKNOWN=0,AI_BOARD_S2,AI_BOARD_WROOM} AiBoardKind;
enum {AI_BOARD_CAP_WIFI=1u,AI_BOARD_CAP_BLE=2u,AI_BOARD_CAP_GPIO=4u,AI_BOARD_CAP_SENSOR=8u};
typedef struct {AiBoardKind kind;unsigned capabilities;} AiBoardIdentity;
static inline bool ai_board_parse(const char* line,AiBoardIdentity* out){
 if(!line||!out)return false;
 size_t n=0;while(n<96&&line[n])n++;if(n==96)return false;
 const char* caps=0;AiBoardKind kind=AI_BOARD_UNKNOWN;
 if(strncmp(line,"BOARD|S2|",9)==0){kind=AI_BOARD_S2;caps=line+9;}
 else if(strncmp(line,"BOARD|WROOM|",12)==0){kind=AI_BOARD_WROOM;caps=line+12;}
 else return false;
 unsigned bits=0;
 while(*caps){const char* end=strchr(caps,',');size_t len=end?(size_t)(end-caps):strlen(caps);
 if(len==4&&strncmp(caps,"WIFI",4)==0)bits|=AI_BOARD_CAP_WIFI;
 else if(len==3&&strncmp(caps,"BLE",3)==0)bits|=AI_BOARD_CAP_BLE;
 else if(len==4&&strncmp(caps,"GPIO",4)==0)bits|=AI_BOARD_CAP_GPIO;
 else if(len==6&&strncmp(caps,"SENSOR",6)==0)bits|=AI_BOARD_CAP_SENSOR;
 if(!end) break;
 caps=end+1;}
 out->kind=kind;out->capabilities=bits;return true;
}
#endif
