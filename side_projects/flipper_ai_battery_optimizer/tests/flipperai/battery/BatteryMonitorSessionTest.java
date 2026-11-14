package flipperai.battery;

import java.util.List;

public final class BatteryMonitorSessionTest {
    private static int checks;
    private static void check(boolean value, String message) {
        checks++;
        if(!value) throw new AssertionError(message);
    }

    private static String telemetry(long id, int percent, boolean charging, boolean active) {
        return "AI1|BAT_TELEM|" + id + "|v1,p=" + percent +
            ",c=" + (charging ? "1" : "0") + ",a=" + (active ? "1" : "0") + "\n";
    }

    public static void main(String[] args) {
        BatteryMonitorSession session = new BatteryMonitorSession();
        check(!session.beginPoll(1, 100L, true, true, false), "no trusted link");
        session.updateLink(21, true, false, 1000L);
        check(!session.beginPoll(1, 1000L, true, true, false), "missing capability");
        session.updateLink(21, true, true, 1000L);
        check(session.isTrustedAndCapable(), "trusted capability");
        check(!session.beginPoll(1, 1000L, false, true, false), "user disabled");
        check(!session.beginPoll(1, 1000L, true, false, false), "background denied");
        check(!session.beginPoll(1, 1000L, true, true, true), "active hardware denied");
        check(!session.beginPoll(0, 1000L, true, true, false), "zero ID denied");
        check(!session.beginPoll(0x100000000L, 1000L, true, true, false), "ID overflow denied");
        check(session.beginPoll(1, 1000L, true, true, false), "initial poll allowed");
        check(session.hasPendingRequest(), "pending state");
        check(!session.beginPoll(2, 1001L, true, true, false), "no concurrent polling");
        check(!session.acceptFrame(telemetry(1, 80, false, false), 1010L, 22), "stale link epoch");
        check(!session.acceptFrame(telemetry(2, 80, false, false), 1010L, 21), "unmatched request ID");
        check(session.hasPendingRequest(), "wrong id must not clear pending");
        check(session.acceptFrame(telemetry(1, 80, false, false), 1010L, 21), "valid sample");
        check(!session.acceptFrame(telemetry(1, 80, false, false), 1011L, 21), "replay after completion");
        check(!session.hasPendingRequest(), "complete request");
        check(session.history().size() == 1, "history collected");
        List<BatteryOptimizer.Sample> history = session.history();
        boolean immutable = false;
        try { history.clear(); } catch(UnsupportedOperationException expected) { immutable = true; }
        check(immutable && session.history().size() == 1, "immutable history");
        check(session.nextPollAtMs() == 1010L + BatteryMonitorSession.NORMAL_INTERVAL_MS,
            "normal spacing");
        check(!session.beginPoll(2, 1020L, true, true, false), "prevent tight polling");
        long secondAt = session.nextPollAtMs();
        check(session.beginPoll(2, secondAt, true, true, false), "eligible scheduled poll");
        check(!session.acceptFrame(telemetry(2, 76, false, false), secondAt - 1, 21),
            "out of order clock");
        check(session.acceptFrame(telemetry(2, 76, false, false), secondAt + 50, 21),
            "second sample");
        check(Double.isNaN(session.estimatedHoursRemaining()), "too little history for estimate");
        long thirdAt = session.nextPollAtMs();
        check(session.beginPoll(3, thirdAt, true, true, false), "third poll");
        check(session.acceptFrame(telemetry(3, 12, false, false), thirdAt + 10, 21),
            "low battery sample");
        check(session.advice(thirdAt + 10).suggestedProfile == BatteryOptimizer.Profile.ECO,
            "eco advice");
        check(!session.advice(thirdAt + 10).automaticApplyAllowed,
            "read only");
        check(session.nextPollAtMs() == thirdAt + 10 + BatteryMonitorSession.CONSERVE_INTERVAL_MS,
            "conserve cadence");
        check(session.advice(thirdAt + 300000L).state == BatteryOptimizer.State.LOW_BATTERY,
            "five-minute cadence is still fresh");
        check(session.advice(thirdAt + BatteryOptimizer.STALE_AFTER_MS + 11L).state ==
            BatteryOptimizer.State.STALE_DATA, "old sample marked stale");
        long fourth = session.nextPollAtMs();
        check(session.beginPoll(4, fourth, true, true, false), "fourth poll");
        session.expireRequest(fourth + BatteryMonitorSession.RESPONSE_TIMEOUT_MS - 1);
        check(session.hasPendingRequest(), "not prematurely timed out");
        session.expireRequest(fourth + BatteryMonitorSession.RESPONSE_TIMEOUT_MS);
        check(!session.hasPendingRequest(), "timeout clears request");
        check(session.consecutiveFailures() == 1, "one failure");
        check(!session.beginPoll(5, fourth + 30001, true, true, false), "backoff enforced");
        long fifth = session.nextPollAtMs();
        check(session.beginPoll(5, fifth, true, true, false), "retry allowed");
        check(!session.acceptFrame("not a frame", fifth + 1, 21), "malformed rejected");
        check(session.consecutiveFailures() == 2, "malformed backoff");
        long sixth = session.nextPollAtMs();
        check(session.beginPoll(6, sixth, true, true, false), "retry after malformed");
        check(session.acceptFrame(telemetry(6, 10, true, true), sixth + 1, 21),
            "charging/active telemetry accepted read-only");
        check(session.advice(sixth + 1).state == BatteryOptimizer.State.CHARGING,
            "charging safety");
        check(session.nextPollAtMs() == sixth + 1 + BatteryMonitorSession.CONSERVE_INTERVAL_MS,
            "charging slower cadence");
        check(session.consecutiveFailures() == 0, "success resets backoff");
        session.updateLink(22, true, true, sixth + 2);
        check(session.history().isEmpty(), "new epoch clears old data");
        check(!session.acceptFrame(telemetry(6, 10, true, true), sixth + 3, 21),
            "old generation rejected");
        session.updateLink(22, false, false, sixth + 4);
        check(!session.isTrustedAndCapable(), "disconnection revokes trust");
        check(!session.beginPoll(7, sixth + 4, true, true, false), "no poll after disconnect");
        System.out.println("PASS BatteryMonitorSessionTest (" + checks + " assertions; host-only)");
    }
}
