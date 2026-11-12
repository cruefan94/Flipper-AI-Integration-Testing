#include "../../flipper_app/satellite_protocol/ai_wire.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void) {
    char b[181];size_t n=0;AiWireMessage msg;
    assert(ai_wire_format(b,sizeof(b),"HELLO",1,"flipper-v1",&n)==AI_WIRE_OK);
    assert(ai_wire_parse((const uint8_t*)b,n,&msg)==AI_WIRE_OK);
    assert(!strcmp(msg.type,"HELLO") && !strcmp(msg.payload,"flipper-v1") && msg.request_id==1);
    assert(ai_wire_parse((const uint8_t*)"AI1|ASK|4294967296|x\n",21,&msg)==AI_WIRE_BAD_ID);
    assert(ai_wire_parse((const uint8_t*)"AI1|ASK|1|x|y\n",14,&msg)==AI_WIRE_BAD_FRAME);
    assert(ai_wire_parse((const uint8_t*)"AI2|ASK|1|x\n",12,&msg)==AI_WIRE_BAD_VERSION);
    /* A rejected wire frame must never overwrite an existing response. */
    memset(&msg,0xA5,sizeof(msg));
    AiWireMessage unchanged=msg;
    const char* bad_id="AI1|ASK|4294967296|x\n";
    assert(ai_wire_parse((const uint8_t*)bad_id,strlen(bad_id),&msg)==AI_WIRE_BAD_ID);
    assert(memcmp(&msg,&unchanged,sizeof(msg))==0);
    const char* bad_payload="AI1|ASK|1|x|y\n";
    assert(ai_wire_parse((const uint8_t*)bad_payload,strlen(bad_payload),&msg)==AI_WIRE_BAD_FRAME);
    assert(memcmp(&msg,&unchanged,sizeof(msg))==0);
    const char* valid="AI1|ANSWER|42|ready\n";
    assert(ai_wire_parse((const uint8_t*)valid,strlen(valid),&msg)==AI_WIRE_OK);
    assert(msg.request_id==42 && !strcmp(msg.type,"ANSWER") && !strcmp(msg.payload,"ready"));
    /* Request ID zero is reserved; rejection must preserve the caller output. */
    AiWireMessage before_zero=msg;
    const char* zero_id="AI1|ANSWER|0|ready\n";
    assert(ai_wire_parse((const uint8_t*)zero_id,strlen(zero_id),&msg)==AI_WIRE_BAD_ID);
    assert(memcmp(&msg,&before_zero,sizeof(msg))==0);
    assert(ai_wire_format(b,sizeof(b),"ASK",0,"question",&n)==AI_WIRE_BAD_ID);
    assert(n==0);
    assert(ai_wire_format(b,sizeof(b),"ASK",5,"x|y",&n)==AI_WIRE_BAD_FRAME);
    assert(ai_wire_format(b,8,"ASK",5,"hello",&n)==AI_WIRE_OVERFLOW);
    /* Overflow must leave both the output bytes and written count unchanged/zero. */
    memset(b,0x5a,sizeof(b));
    n=123;
    assert(ai_wire_format(b,8,"ASK",5,"hello",&n)==AI_WIRE_OVERFLOW);
    assert(n==0);
    for(size_t i=0;i<sizeof(b);i++)assert((unsigned char)b[i]==0x5a);
    assert(ai_wire_format(b,sizeof(b),"ASK",5,"hello",&n)==AI_WIRE_OK);
    assert(n==strlen("AI1|ASK|5|hello\n"));
    assert(b[n-1]=='\n' && b[n]=='\0');
    assert(ai_wire_parse((const uint8_t*)b,n,&msg)==AI_WIRE_OK);
    assert(msg.request_id==5 && !strcmp(msg.payload,"hello"));
    /* Boundary: 180-byte frames are accepted, 181-byte frames are rejected.
     * ASK with one-digit ID has an 11-byte framing overhead. */
    char payload[AI_WIRE_MAX_FRAME + 2u];
    memset(payload,'a',sizeof(payload));
    payload[AI_WIRE_MAX_FRAME-11u]='\0';
    assert(ai_wire_format(b,sizeof(b),"ASK",5,payload,&n)==AI_WIRE_OK);
    assert(n==AI_WIRE_MAX_FRAME);
    assert(ai_wire_parse((const uint8_t*)b,n,&msg)==AI_WIRE_OK);
    assert(strlen(msg.payload)==AI_WIRE_MAX_FRAME-11u);
    payload[AI_WIRE_MAX_FRAME-11u]='a';
    payload[AI_WIRE_MAX_FRAME-10u]='\0';
    memset(b,0x5a,sizeof(b));
    n=999;
    assert(ai_wire_format(b,sizeof(b),"ASK",5,payload,&n)==AI_WIRE_OVERFLOW);
    assert(n==0);
    for(size_t i=0;i<sizeof(b);i++)assert((unsigned char)b[i]==0x5a);
    /* Oversized input must be rejected without mutating the response. */
    uint8_t oversized[AI_WIRE_MAX_FRAME+1u];
    memset(oversized,'x',sizeof(oversized));
    oversized[sizeof(oversized)-1u]='\n';
    AiWireMessage previous=msg;
    assert(ai_wire_parse(oversized,sizeof(oversized),&msg)==AI_WIRE_BAD_FRAME);
    assert(memcmp(&msg,&previous,sizeof(msg))==0);
    /* Bounded input scans reject oversized strings before formatting. */
    char too_long[AI_WIRE_MAX_FRAME+32u];
    memset(too_long,'q',sizeof(too_long));
    too_long[sizeof(too_long)-1u]='\0';
    memset(b,0x5a,sizeof(b));
    n=123;
    assert(ai_wire_format(b,sizeof(b),"ASK",7,too_long,&n)==AI_WIRE_OVERFLOW);
    assert(n==0);
    for(size_t i=0;i<sizeof(b);i++)assert((unsigned char)b[i]==0x5a);
    char bad_type[AI_WIRE_MAX_TYPE+3u];
    memset(bad_type,'A',sizeof(bad_type));
    bad_type[sizeof(bad_type)-1u]='\0';
    assert(ai_wire_format(b,sizeof(b),bad_type,7,"ok",&n)==AI_WIRE_BAD_TYPE);
    assert(n==0);
    puts("ai_wire native tests passed");return 0;
}
