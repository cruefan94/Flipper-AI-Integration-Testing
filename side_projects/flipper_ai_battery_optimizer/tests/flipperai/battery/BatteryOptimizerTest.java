package flipperai.battery;

import java.util.Arrays;
import java.util.Collections;

public final class BatteryOptimizerTest {
    private static int assertions = 0;
    private static void check(boolean condition, String message) {
        assertions++;
        if(!condition) throw new AssertionError(message);
    }
    private static BatteryOptimizer.Sample sample(long ms, int pct, boolean charging, boolean busy) {
        return new BatteryOptimizer.Sample(ms, pct, 96, 23.5, charging, busy);
    }
    public static void main(String[] args) {
        long now = 10000000L;
        check(BatteryOptimizer.evaluate(null, now).state == BatteryOptimizer.State.NO_DATA, "missing sample");
        check(BatteryOptimizer.evaluate(sample(now - BatteryOptimizer.STALE_AFTER_MS - 1, 50, false, false), now).state ==
              BatteryOptimizer.State.STALE_DATA, "stale sample");
        check(BatteryOptimizer.evaluate(sample(now, -1, false, false), now).state ==
              BatteryOptimizer.State.INVALID_DATA, "invalid percent");
        check(BatteryOptimizer.evaluate(sample(now + 1, 20, false, false), now).state ==
              BatteryOptimizer.State.INVALID_DATA, "future sample");
        check(BatteryOptimizer.evaluate(sample(now, 10, true, false), now).state ==
              BatteryOptimizer.State.CHARGING, "charging priority");
        check(BatteryOptimizer.evaluate(sample(now, 10, false, true), now).state ==
              BatteryOptimizer.State.HARDWARE_BUSY, "active hardware operation");
        BatteryOptimizer.Advice low = BatteryOptimizer.evaluate(sample(now, 10, false, false), now);
        check(low.state == BatteryOptimizer.State.LOW_BATTERY, "low battery");
        check(low.suggestedProfile == BatteryOptimizer.Profile.ECO, "eco profile");
        check(!low.automaticApplyAllowed, "no automatic hardware writes");
        check(low.suggestedTelemetryIntervalSeconds >= 180, "avoid expensive polling");
        check(BatteryOptimizer.evaluate(sample(now, 63, false, false), now).suggestedProfile ==
              BatteryOptimizer.Profile.BALANCED, "balanced profile");
        check(BatteryOptimizer.evaluate(sample(now, 98, false, false), now).suggestedProfile ==
              BatteryOptimizer.Profile.PERFORMANCE, "performance profile");
        BatteryOptimizer.Sample hot = new BatteryOptimizer.Sample(now, 80, 95, 52.0, false, false);
        check(BatteryOptimizer.evaluate(hot, now).state ==
              BatteryOptimizer.State.THERMAL_WARNING, "thermal guard");
        BatteryOptimizer.Sample badTemperature = new BatteryOptimizer.Sample(now, 80, null, Double.NaN, false, false);
        check(BatteryOptimizer.evaluate(badTemperature, now).state ==
              BatteryOptimizer.State.INVALID_DATA, "nan reject");
        double estimate = BatteryOptimizer.estimatedHoursRemaining(Arrays.asList(
            sample(0L, 80, false, false), sample(3600000L, 74, false, false)));
        check(Math.abs(estimate - 74.0 / 6.0) < 0.001, "discharge estimate");
        check(Double.isNaN(BatteryOptimizer.estimatedHoursRemaining(Arrays.asList(
            sample(0L, 80, false, false), sample(60000L, 79, false, false)))), "too short");
        check(Double.isNaN(BatteryOptimizer.estimatedHoursRemaining(Arrays.asList(
            sample(0L, 80, false, false), sample(3600000L, 81, false, false)))), "charge rise");
        check(Double.isNaN(BatteryOptimizer.estimatedHoursRemaining(Arrays.asList(
            sample(0L, 80, false, false), sample(3600000L, 74, true, false)))), "charging estimate");
        check(Double.isNaN(BatteryOptimizer.estimatedHoursRemaining(Collections.emptyList())), "no history");
        System.out.println("PASS BatteryOptimizerTest (" + assertions + " assertions; host-only)");
    }
}
