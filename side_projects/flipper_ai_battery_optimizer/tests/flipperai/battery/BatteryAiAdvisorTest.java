package flipperai.battery;

public final class BatteryAiAdvisorTest {
    private static int checks;
    private static void check(boolean value, String name) {
        checks++;
        if(!value) throw new AssertionError(name);
    }
    public static void main(String[] args) {
        final int[] calls = {0};
        final String[] last = {null};
        BatteryAiAdvisor.TextEngine local = new BatteryAiAdvisor.TextEngine() {
            @Override public String explain(String prompt) {
                calls[0]++;
                last[0] = prompt;
                return "The battery is low. Consider Eco mode.";
            }
        };
        BatteryOptimizer.Sample sample = new BatteryOptimizer.Sample(
            1000L, 10, null, null, false, false);
        BatteryAiAdvisor.Result onlineDenied = BatteryAiAdvisor.explain(
            sample, 1000L, BatteryAiAdvisor.Execution.ONLINE, false, local);
        check(onlineDenied.outcome == BatteryAiAdvisor.Outcome.NOT_AUTHORIZED,
            "separate cloud authorization");
        check(calls[0] == 0, "no unauthorized AI call");
        check(onlineDenied.safeAdvice.suggestedProfile == BatteryOptimizer.Profile.ECO,
            "safe policy remains available");

        BatteryAiAdvisor.Result offline = BatteryAiAdvisor.explain(
            sample, 1000L, BatteryAiAdvisor.Execution.OFFLINE, false, local);
        check(offline.outcome == BatteryAiAdvisor.Outcome.EXPLAINED, "offline provider used");
        check(calls[0] == 1 && last[0].contains("Battery=10%"), "bounded local facts");
        check(last[0].contains("health=unknown") && last[0].contains("temperature=unknown"),
            "does not invent sensor readings");
        check(!offline.safeAdvice.automaticApplyAllowed, "AI cannot enable actions");

        BatteryAiAdvisor.Result cloudApproved = BatteryAiAdvisor.explain(
            sample, 1000L, BatteryAiAdvisor.Execution.ONLINE, true, local);
        check(cloudApproved.outcome == BatteryAiAdvisor.Outcome.EXPLAINED &&
              calls[0] == 2, "cloud call requires consent");
        BatteryAiAdvisor.Result stale = BatteryAiAdvisor.explain(
            sample, 1000L + BatteryOptimizer.STALE_AFTER_MS + 1L,
            BatteryAiAdvisor.Execution.OFFLINE, false, local);
        check(stale.outcome == BatteryAiAdvisor.Outcome.DETERMINISTIC_FALLBACK &&
              calls[0] == 2, "no inference on stale reading");
        BatteryAiAdvisor.Result unavailable = BatteryAiAdvisor.explain(
            sample, 1000L, BatteryAiAdvisor.Execution.OFFLINE, false,
            new BatteryAiAdvisor.TextEngine() {
                @Override public String explain(String prompt) throws Exception {
                    throw new Exception("model unavailable");
                }
            });
        check(unavailable.outcome == BatteryAiAdvisor.Outcome.DETERMINISTIC_FALLBACK,
            "model failures fallback");
        BatteryAiAdvisor.Result oversized = BatteryAiAdvisor.explain(
            sample, 1000L, BatteryAiAdvisor.Execution.OFFLINE, false,
            new BatteryAiAdvisor.TextEngine() {
                @Override public String explain(String prompt) {
                    StringBuilder s = new StringBuilder();
                    for(int i=0;i<600;i++) s.append('x');
                    return s.toString();
                }
            });
        check(oversized.outcome == BatteryAiAdvisor.Outcome.DETERMINISTIC_FALLBACK,
            "oversized AI answer discarded");
        check(BatteryAiAdvisor.explain(null, 1000L,
            BatteryAiAdvisor.Execution.OFFLINE, false, local).outcome ==
            BatteryAiAdvisor.Outcome.DETERMINISTIC_FALLBACK, "missing data fallback");
        check(calls[0] == 2, "no model call with missing data");
        System.out.println("PASS BatteryAiAdvisorTest (" + checks + " assertions)");
    }
}
