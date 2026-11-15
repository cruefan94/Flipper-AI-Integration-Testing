#include <assert.h>
#include <string.h>
#include "ai_board_link.h"
int main(void) {
 AiBoardIdentity b={0};
 assert(ai_board_parse("BOARD|S2|WIFI,GPIO",&b));
 assert(b.kind==AI_BOARD_S2 && b.capabilities==(AI_BOARD_CAP_WIFI|AI_BOARD_CAP_GPIO));
 assert(ai_board_parse("BOARD|WROOM|WIFI,BLE,GPIO,SENSOR",&b));
 assert(b.kind==AI_BOARD_WROOM && b.capabilities==15u);
 assert(!ai_board_parse("BOARD|WROOM",&b));
 assert(!ai_board_parse("BOARD|BAD|WIFI",&b));
 assert(!ai_board_parse(0,&b));
 assert(!ai_board_parse("BOARD|S2|WIFI",0));
 char longline[100];memset(longline,'A',99);longline[99]=0;
 assert(!ai_board_parse(longline,&b));
 return 0;
}
