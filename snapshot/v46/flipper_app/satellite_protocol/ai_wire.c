#include "ai_wire.h"
#include <stdio.h>
#include <string.h>
#include <limits.h>
static int type_valid(const char* s, size_t n) {
    if(n == 0 || n > AI_WIRE_MAX_TYPE) return 0;
    for(size_t i=0;i<n;i++) if(!((s[i]>='A'&&s[i]<='Z')||s[i]=='_')) return 0;
    return 1;
}
static int payload_valid(const char* s, size_t n) {
    for(size_t i=0;i<n;i++) if(s[i]=='|' || s[i]=='\n' || s[i]=='\r' || s[i]=='\0') return 0;
    return 1;
}
AiWireResult ai_wire_parse(const uint8_t* data,size_t length,AiWireMessage* out) {
    if(!data || !out || length < 8 || length > AI_WIRE_MAX_FRAME || data[length-1]!='\n') return AI_WIRE_BAD_FRAME;
    /* Parse transactionally: rejected frames must not alter caller output. */
    AiWireMessage parsed = {0};
    for(size_t i=0;i<length;i++) if(data[i]==0 || data[i]=='\r') return AI_WIRE_BAD_FRAME;
    if(memcmp(data,"AI1|",4)!=0) return AI_WIRE_BAD_VERSION;
    size_t first=4;
    while(first<length && data[first]!='|')first++;
    if(first==length || !type_valid((const char*)data+4,first-4))return AI_WIRE_BAD_TYPE;
    memcpy(parsed.type,data+4,first-4);
    size_t second=first+1;
    while(second<length && data[second]!='|')second++;
    if(second==length || second==first+1 || second-first-1>10)return AI_WIRE_BAD_ID;
    uint32_t id=0;
    for(size_t i=first+1;i<second;i++) {
        if(data[i]<'0'||data[i]>'9')return AI_WIRE_BAD_ID;
        uint32_t digit=(uint32_t)(data[i]-'0');
        if(id>(UINT32_MAX-digit)/10u)return AI_WIRE_BAD_ID;
        id=id*10u+digit;
    }
    /* Zero is reserved: requests and responses use nonzero IDs. */
    if(id==0)return AI_WIRE_BAD_ID;
    parsed.request_id=id;
    size_t p=second+1, n=length-1-p;
    if(!payload_valid((const char*)data+p,n))return AI_WIRE_BAD_FRAME;
    memcpy(parsed.payload,data+p,n);
    *out=parsed;
    return AI_WIRE_OK;
}
AiWireResult ai_wire_format(char* out,size_t capacity,const char* type,uint32_t id,const char* payload,size_t* written) {
    if(written)*written=0;
    if(!out || !type || !payload || !capacity)return AI_WIRE_BAD_FRAME;
    /* Bound input scanning before formatting; oversized strings cannot produce
     * a valid 180-byte frame and must not trigger unbounded strlen/snprintf. */
    size_t t=0,p=0;
    while(t<=AI_WIRE_MAX_TYPE && type[t]!='\0')t++;
    if(!type_valid(type,t))return AI_WIRE_BAD_TYPE;
    if(id==0)return AI_WIRE_BAD_ID;
    while(p<=AI_WIRE_MAX_FRAME && payload[p]!='\0')p++;
    if(p>AI_WIRE_MAX_FRAME)return AI_WIRE_OVERFLOW;
    if(!payload_valid(payload,p))return AI_WIRE_BAD_FRAME;
    /* Never leave a truncated or partial frame in the caller's buffer. */
    char frame[AI_WIRE_MAX_FRAME+1u];
    int n=snprintf(frame,sizeof(frame),"AI1|%s|%lu|%s\n",type,(unsigned long)id,payload);
    if(n<0 || (size_t)n>AI_WIRE_MAX_FRAME || (size_t)n>=capacity)return AI_WIRE_OVERFLOW;
    memcpy(out,frame,(size_t)n+1u);
    if(written)*written=(size_t)n;
    return AI_WIRE_OK;
}
