#include "../../flipper_app/satellite_protocol/ai_link.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
typedef struct {char frame[181];size_t length;int count;bool accept;} Fake;
static bool write_frame(const uint8_t* frame,size_t length,void* context){
 Fake* f=context;f->count++;if(!f->accept)return false;
 memcpy(f->frame,frame,length);f->frame[length]=0;f->length=length;return true;
}
int main(void){
 Fake f={.accept=true};AiLink link;AiWireMessage reply;
 ai_link_init(&link,write_frame,&f);
 assert(ai_link_hello(&link)==AI_CLIENT_NOT_READY);
 ai_link_connection(&link,true,20);
 assert(ai_link_hello(&link)==AI_CLIENT_NO_SPACE);
 assert(f.count==0);
 ai_link_connection(&link,false,0);
 ai_link_connection(&link,true,180);
 assert(ai_link_hello(&link)==AI_CLIENT_OK);
 assert(strcmp(f.frame,"AI1|HELLO|1|flipper-v1\n")==0);
 assert(ai_link_hello(&link)==AI_CLIENT_BUSY);
 const char* hello="AI1|HELLO_ACK|1|android-v1\n";
 assert(ai_link_notification(&link,(const uint8_t*)hello,strlen(hello),&reply)==AI_CLIENT_NOT_READY);
 ai_link_write_complete(&link,true);
 assert(ai_link_notification(&link,(const uint8_t*)hello,strlen(hello),&reply)==AI_CLIENT_OK);
 assert(ai_link_ask(&link,"battery help")==AI_CLIENT_OK);
 ai_link_write_complete(&link,false);
 assert(link.client.phase==AI_CLIENT_DISCONNECTED);
 ai_link_connection(&link,false,0);
 ai_link_connection(&link,true,180);
 f.accept=false;
 assert(ai_link_hello(&link)==AI_CLIENT_NO_SPACE);
 assert(link.client.phase==AI_CLIENT_DISCONNECTED);
 ai_link_connection(&link,false,0);
 assert(ai_link_hello(&link)==AI_CLIENT_NOT_READY);
 f.accept=true;
 ai_link_connection(&link,true,180);
 assert(ai_link_hello(&link)==AI_CLIENT_OK);
 ai_link_set_deadline(&link,0xfffffff0u,50);
 /* A second scheduling attempt must not extend the original deadline. */
 ai_link_set_deadline(&link,0x00000010u,50);
 assert(link.deadline_ms==0x00000022u);
 assert(!ai_link_poll_timeout(&link,0x00000010u));
 assert(ai_link_poll_timeout(&link,0x00000023u));
 assert(!link.write_pending);
 assert(link.client.phase==AI_CLIENT_DISCONNECTED);
 assert(ai_link_notification(&link,(const uint8_t*)hello,strlen(hello),&reply)==AI_CLIENT_NOT_READY);
 assert(ai_link_hello(&link)==AI_CLIENT_NOT_READY);
 ai_link_connection(&link,true,180);
 assert(ai_link_hello(&link)==AI_CLIENT_NOT_READY);
 ai_link_connection(&link,false,0);
 ai_link_connection(&link,true,180);
 assert(ai_link_hello(&link)==AI_CLIENT_OK);
 ai_link_set_deadline(&link,100,50);
 ai_link_write_complete(&link,true);
 assert(ai_link_notification(&link,(const uint8_t*)hello,strlen(hello),&reply)==AI_CLIENT_OK);
 assert(!ai_link_poll_timeout(&link,200));
 /* Exactly half a 32-bit clock cycle before the deadline is not expired. */
 ai_link_connection(&link,false,0);
 ai_link_connection(&link,true,180);
 assert(ai_link_hello(&link)==AI_CLIENT_OK);
 ai_link_set_deadline(&link,0xfffffff0u,50u);
 assert(link.deadline_ms==0x22u);
 assert(!ai_link_poll_timeout(&link,0x80000022u));
 assert(!ai_link_poll_timeout(&link,0x21u));
 assert(ai_link_poll_timeout(&link,0x22u));

 /* Repeated connected events must preserve the outstanding handshake and timeout. */
 ai_link_connection(&link,false,0);
 ai_link_connection(&link,true,180);
 assert(ai_link_hello(&link)==AI_CLIENT_OK);
 ai_link_set_deadline(&link,100u,50u);
 unsigned pending=link.client.pending_id;
 ai_link_connection(&link,true,180);
 assert(link.write_pending);
 assert(link.deadline_active && link.deadline_ms==150u);
 assert(link.client.pending_id==pending);
 assert(link.client.phase==AI_CLIENT_HANDSHAKE_PENDING);
 ai_link_write_complete(&link,true);
 assert(ai_link_notification(&link,(const uint8_t*)hello,strlen(hello),&reply)==AI_CLIENT_OK);
 assert(link.client.phase==AI_CLIENT_READY);
 /* A repeated connected callback must not reset a ready session either. */
 ai_link_connection(&link,true,180);
 assert(link.client.phase==AI_CLIENT_READY);
 assert(ai_link_ask(&link,"ping")==AI_CLIENT_OK);
 ai_link_connection(&link,true,180);
 assert(link.client.phase==AI_CLIENT_ASK_PENDING && link.write_pending);
 ai_link_connection(&link,false,0);
 assert(link.client.phase==AI_CLIENT_DISCONNECTED);

 /* MTU changes during an in-flight exchange must require reconnection. */
 ai_link_connection(&link,true,180);
 assert(ai_link_hello(&link)==AI_CLIENT_OK);
 ai_link_set_deadline(&link,100u,50u);
 ai_link_connection(&link,true,80);
 assert(link.reconnect_required && !link.connected);
 assert(!link.write_pending && !link.deadline_active);
 assert(link.client.phase==AI_CLIENT_DISCONNECTED);
 assert(ai_link_hello(&link)==AI_CLIENT_NOT_READY);
 ai_link_connection(&link,true,180);
 assert(ai_link_hello(&link)==AI_CLIENT_NOT_READY);
 ai_link_connection(&link,false,0);
 ai_link_connection(&link,true,180);
 assert(ai_link_hello(&link)==AI_CLIENT_OK);
 ai_link_write_complete(&link,true);
 assert(ai_link_notification(&link,(const uint8_t*)hello,strlen(hello),&reply)==AI_CLIENT_OK);
 assert(ai_link_ask(&link,"battery")==AI_CLIENT_OK);
 ai_link_connection(&link,true,80);
 assert(link.reconnect_required && !link.connected);
 ai_link_connection(&link,false,0);
 ai_link_connection(&link,true,180);
 assert(ai_link_hello(&link)==AI_CLIENT_OK);
 ai_link_write_complete(&link,true);
 assert(ai_link_notification(&link,(const uint8_t*)hello,strlen(hello),&reply)==AI_CLIENT_OK);
 /* An idle MTU update can reset the session without faulting the link. */
 ai_link_connection(&link,true,80);
 assert(link.connected && !link.reconnect_required);
 assert(link.client.phase==AI_CLIENT_DISCONNECTED);

 puts("ai_link native tests passed");return 0;
}
