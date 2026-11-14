package flipperai.battery;

public final class BatteryReadTransportTest {
    private static int assertions;
    private static void check(boolean cond, String message) {
        assertions++;
        if(!cond) throw new AssertionError(message);
    }
    private static final class Sender implements BatteryReadTransport.FrameSender {
        int sends;
        boolean accept = true;
        boolean throwError;
        String latest;
        @Override public boolean send(String frame) {
            sends++;
            latest = frame;
            if(throwError) throw new IllegalStateException("BLE unavailable");
            return accept;
        }
    }
    public static void main(String[] args) {
        BatteryReadTransport transport = new BatteryReadTransport();
        Sender sender = new Sender();
        transport.updateTrustedLink(3L,true,true,1000L);
        check(!transport.pollIfDue(7L,1000L,true,false,sender), "opt-in required");
        check(sender.sends == 0, "must not send before consent");

        transport.setUserOptIn(true);
        transport.updateTrustedLink(3L,true,false,1000L);
        check(!transport.pollIfDue(7L,1000L,true,false,sender), "capability required");
        transport.updateTrustedLink(3L,false,true,1000L);
        check(!transport.pollIfDue(7L,1000L,true,false,sender), "authenticated link required");

        transport.updateTrustedLink(3L,true,true,1000L);
        check(!transport.pollIfDue(7L,1000L,false,false,sender), "foreground required");
        check(!transport.pollIfDue(7L,1000L,true,true,sender), "busy device guard");

        sender.accept = false;
        check(!transport.pollIfDue(7L,1000L,true,false,sender), "reject failed write");
        check(transport.failures() == 1 && !transport.hasPendingRequest(), "failed write backoff");
        check(!transport.receiveFrame("AI1|BAT_TELEM|7|v1,p=80,c=0,a=0\n",
              1001L, 3L), "late frame from rejected write");

        long next = transport.nextPollAtMs();
        sender.accept = true;
        check(transport.pollIfDue(8L,next,true,false,sender), "retry after backoff");
        check("AI1|BAT_GET|8|v1\n".equals(sender.latest), "canonical request frame");
        check(transport.hasPendingRequest(), "pending until response");
        check(!transport.receiveFrame("AI1|BAT_TELEM|8|v1,p=80,c=0,a=0\n",
              next+1L,4L), "epoch correlation");
        check(transport.receiveFrame("AI1|BAT_TELEM|8|v1,p=80,c=0,a=0\n",
              next+2L,3L), "matching read-only response");
        check(transport.history().size() == 1, "stores reading in memory");
        check(transport.advice(next+2L).suggestedProfile == BatteryOptimizer.Profile.PERFORMANCE,
              "recommendation available");

        long second = transport.nextPollAtMs();
        check(transport.pollIfDue(9L,second,true,false,sender), "second request started");
        transport.onBackground();
        check(!transport.hasPendingRequest(), "background cancels pending request");
        check(!transport.receiveFrame("AI1|BAT_TELEM|9|v1,p=79,c=0,a=0\n",
              second+1L,3L), "late frame rejected after background");
        check(transport.history().size() == 1, "history survives temporary background");

        sender.throwError = true;
        check(!transport.pollIfDue(10L,second,true,false,sender), "send exception denied");
        check(transport.failures() == 1, "failed queue submission tracked");
        sender.throwError = false;

        transport.setUserOptIn(false);
        check(transport.history().isEmpty(), "opt-out deletes history");
        check(!transport.pollIfDue(11L,second+100000L,true,false,sender),
              "opt-out prevents further sending");
        check(transport.advice(second+100000L).state == BatteryOptimizer.State.NO_DATA,
              "opt-out cannot display stale recommendation");
        check(Double.isNaN(transport.estimatedHoursRemaining()), "opt-out clears estimate");

        transport.setUserOptIn(true);
        transport.updateTrustedLink(4L,true,true,second+100000L);
        check(transport.pollIfDue(1L,second+100000L,true,false,sender),
              "new connection permits fresh request counter");
        transport.onDisconnect();
        check(!transport.receiveFrame("AI1|BAT_TELEM|1|v1,p=60,c=0,a=0\n",
              second+100001L,4L), "disconnect ignores delayed frame");
        check(transport.history().isEmpty(), "no cross-session cached history");
        transport.updateTrustedLink(4L, true, true, second+100002L);
        check(!transport.pollIfDue(2L,second+100002L,true,false,sender),
              "old BLE epoch rejected even after reconnect");
        transport.updateTrustedLink(5L, true, true, second+100003L);
        check(transport.pollIfDue(1L,second+100003L,true,false,sender),
              "fresh BLE epoch allowed");
        System.out.println("PASS BatteryReadTransportTest (" + assertions + " assertions)");
    }
}
