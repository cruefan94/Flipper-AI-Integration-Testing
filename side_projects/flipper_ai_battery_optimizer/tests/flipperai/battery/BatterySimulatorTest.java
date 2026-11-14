package flipperai.battery;

public final class BatterySimulatorTest {
    private static int checks;
    private static void check(boolean cond, String message) {
        checks++;
        if(!cond) throw new AssertionError(message);
    }
    public static void main(String[] args) {
        String low = BatterySimulator.render(10, false, false, null);
        check(low.contains("SIMULATED"), "explicit synthetic fixture label");
        check(low.contains("LOW_BATTERY"), "low battery state");
        check(low.contains("ECO"), "eco recommendation");
        check(low.contains("Automatic device changes: no"), "no actions");
        String charging = BatterySimulator.render(10, true, false, null);
        check(charging.contains("State: CHARGING") &&
            charging.contains("Profile suggestion: none"), "charging blocks changes");
        String busy = BatterySimulator.render(10, false, true, null);
        check(busy.contains("State: HARDWARE_BUSY"), "active hardware no changes");
        String hot = BatterySimulator.render(95, false, false, 54.0);
        check(hot.contains("State: THERMAL_WARNING"), "thermal guard");
        String invalid = BatterySimulator.render(101, false, false, null);
        check(invalid.contains("State: INVALID_DATA"), "invalid sample");
        System.out.println("PASS BatterySimulatorTest (" + checks + " assertions)");
    }
}
