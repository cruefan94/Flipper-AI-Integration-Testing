package flipperai.battery;

import java.util.Locale;

/**
 * Runnable host-only example of the policy engine, NOT live Flipper telemetry.
 * Requires only a JDK; no model, phone, network or firmware is contacted.
 */
public final class BatterySimulator {
    private BatterySimulator() {}

    public static String render(int batteryPct, boolean charging,
                                boolean hardwareBusy, Double temperatureC) {
        BatteryOptimizer.Sample sample = new BatteryOptimizer.Sample(
            1000L, batteryPct, null, temperatureC, charging, hardwareBusy);
        BatteryOptimizer.Advice advice = BatteryOptimizer.evaluate(sample, 1000L);
        String profile = advice.suggestedProfile == null ? "none" : advice.suggestedProfile.name();
        return String.format(Locale.ROOT,
            "SIMULATED BATTERY READING%nState: %s%nProfile suggestion: %s%n" +
            "Display timeout suggestion: %d s%nTelemetry interval suggestion: %d s%n" +
            "Reason: %s%nAutomatic device changes: %s%n",
            advice.state.name(), profile,
            advice.suggestedDisplayTimeoutSeconds, advice.suggestedTelemetryIntervalSeconds,
            advice.explanation, advice.automaticApplyAllowed ? "yes" : "no");
    }

    public static void main(String[] args) {
        if(args.length < 1 || args.length > 4) {
            System.err.println("Usage: BatterySimulator BATTERY_PERCENT [charging:0|1] " +
                "[hardwareBusy:0|1] [temperatureC]");
            System.exit(2);
        }
        try {
            int percent = Integer.parseInt(args[0]);
            if(percent < 0 || percent > 100) throw new IllegalArgumentException("battery");
            boolean charging = args.length > 1 && strictBit(args[1]);
            boolean busy = args.length > 2 && strictBit(args[2]);
            Double temp = args.length > 3 ? Double.valueOf(args[3]) : null;
            System.out.print(render(percent, charging, busy, temp));
        } catch(RuntimeException badInput) {
            System.err.println("Invalid simulated battery input.");
            System.exit(2);
        }
    }

    private static boolean strictBit(String value) {
        if("0".equals(value)) return false;
        if("1".equals(value)) return true;
        throw new IllegalArgumentException("expected 0 or 1");
    }
}
