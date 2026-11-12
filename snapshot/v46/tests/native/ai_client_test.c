#include "../../flipper_app/satellite_protocol/ai_client.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
int main(void) {
 AiClient c;AiWireMessage msg;char buf[181];size_t n;
 ai_client_reset(&c);
 assert(ai_client_ask(&c,"battery",buf,sizeof buf,&n)==AI_CLIENT_NOT_READY);
 assert(ai_client_hello(&c,buf,sizeof buf,&n)==AI_CLIENT_OK);
 assert(strcmp(buf,"AI1|HELLO|1|flipper-v1\n")==0);
 assert(ai_client_hello(&c,buf,sizeof buf,&n)==AI_CLIENT_BUSY);
 const char* wrong="AI1|HELLO_ACK|2|android-v1\n";
 memset(&msg,0x5a,sizeof msg);
 AiWireMessage unchanged=msg;
 assert(ai_client_receive(&c,(const uint8_t*)wrong,strlen(wrong),&msg)==AI_CLIENT_BAD_RESPONSE);
 assert(memcmp(&msg,&unchanged,sizeof msg)==0);
 const char* wrong_type="AI1|ANSWER|1|premature answer\n";
 assert(ai_client_receive(&c,(const uint8_t*)wrong_type,strlen(wrong_type),&msg)==AI_CLIENT_BAD_RESPONSE);
 assert(memcmp(&msg,&unchanged,sizeof msg)==0);
 const char* hello="AI1|HELLO_ACK|1|android-v1\n";
 assert(ai_client_receive(&c,(const uint8_t*)hello,strlen(hello),&msg)==AI_CLIENT_OK);
 assert(ai_client_ask(&c,"battery help",buf,sizeof buf,&n)==AI_CLIENT_OK);
 assert(strcmp(buf,"AI1|ASK|2|battery help\n")==0);
 const char* answer="AI1|ANSWER|2|Check USB cable\n";
 assert(ai_client_receive(&c,(const uint8_t*)answer,strlen(answer),&msg)==AI_CLIENT_OK);
 assert(strcmp(msg.payload,"Check USB cable")==0);
 assert(strcmp(msg.type,"ANSWER")==0);
 ai_client_reset(&c);
 /* A rollover must not issue ID 0 or mutate the handshake state. */
 c.next_id=0;
 assert(ai_client_hello(&c,buf,sizeof buf,&n)==AI_CLIENT_NOT_READY);
 assert(c.next_id==0 && c.pending_id==0 && c.phase==AI_CLIENT_DISCONNECTED && n==0);
 c.next_id=UINT32_MAX;
 assert(ai_client_hello(&c,buf,sizeof buf,&n)==AI_CLIENT_NOT_READY);
 assert(c.next_id==UINT32_MAX && c.pending_id==0 && c.phase==AI_CLIENT_DISCONNECTED && n==0);
 c.next_id=UINT32_MAX-1u;
 assert(ai_client_hello(&c,buf,sizeof buf,&n)==AI_CLIENT_OK);
 assert(c.pending_id==UINT32_MAX-1u && c.next_id==UINT32_MAX);
 assert(ai_client_receive(&c,(const uint8_t*)"AI1|HELLO_ACK|4294967294|android-v1\n",
     strlen("AI1|HELLO_ACK|4294967294|android-v1\n"),&msg)==AI_CLIENT_OK);
 assert(ai_client_ask(&c,"battery",buf,sizeof buf,&n)==AI_CLIENT_NOT_READY);
 c.next_id=0;
 assert(ai_client_ask(&c,"battery",buf,sizeof buf,&n)==AI_CLIENT_NOT_READY);
 assert(c.phase==AI_CLIENT_READY && c.pending_id==UINT32_MAX-1u && n==0);
 puts("ai_client native tests passed");return 0;
}
