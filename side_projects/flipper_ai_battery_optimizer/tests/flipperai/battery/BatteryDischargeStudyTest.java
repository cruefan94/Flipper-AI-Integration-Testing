package flipperai.battery;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public final class BatteryDischargeStudyTest {
    private static int checks;
    private static void check(boolean value, String message) {
        checks++;
        if(!value) throw new AssertionError(message);
    }
    private static BatteryDischargeStudy.Trial trial(String tag, long duration, int start,
            int end, boolean charging, boolean interrupted) {
        return new BatteryDischargeStudy.Trial(tag, duration, start, end, charging, interrupted);
    }
    private static List<BatteryDischargeStudy.Trial> group(int drop) {
        return Arrays.asList(
            trial("ble_idle", 3600000L, 80, 80-drop, false, false),
            trial("ble_idle", 3600000L, 81, 81-drop, false, false),
            trial("ble_idle", 3600000L, 82, 82-drop, false, false));
    }
    public static void main(String[] args) {
        BatteryDischargeStudy.Result tooFew = BatteryDischargeStudy.compare(
            Collections.<BatteryDischargeStudy.Trial>emptyList(), group(5));
        check(tooFew.status == BatteryDischargeStudy.Status.INSUFFICIENT_DATA,
            "requires multiple trials");
        check(Double.isNaN(tooFew.provisionalRateChangePct), "no fabricated estimate");
        BatteryDischargeStudy.Result result = BatteryDischargeStudy.compare(group(6), group(5));
        check(result.status == BatteryDischargeStudy.Status.PROVISIONAL_COMPARISON,
            "provisional only");
        check(Math.abs(result.baselinePctPointsPerHour - 6.0) < 0.001,
            "baseline median");
        check(Math.abs(result.candidatePctPointsPerHour - 5.0) < 0.001,
            "candidate median");
        check(Math.abs(result.provisionalRateChangePct - (100.0/6.0)) < 0.001,
            "relative discharge comparison");
        check(result.limitation.contains("Preliminary"), "state measurement caveats");
        BatteryDischargeStudy.Result worse = BatteryDischargeStudy.compare(group(5), group(6));
        check(worse.provisionalRateChangePct < 0.0, "candidate can be worse");
        check(BatteryDischargeStudy.compare(group(6),
            Arrays.asList(trial("radio_active",3600000L,80,75,false,false),
                trial("radio_active",3600000L,81,76,false,false),
                trial("radio_active",3600000L,82,77,false,false))).status ==
            BatteryDischargeStudy.Status.NOT_COMPARABLE, "different workload");
        check(BatteryDischargeStudy.compare(group(6),
            Arrays.asList(trial("ble_idle",600000L,80,75,false,false),
                trial("ble_idle",3600000L,81,76,false,false),
                trial("ble_idle",3600000L,82,77,false,false))).status ==
            BatteryDischargeStudy.Status.NOT_COMPARABLE, "short duration rejected");
        check(BatteryDischargeStudy.compare(group(6),
            Arrays.asList(trial("ble_idle",3600000L,80,75,true,false),
                trial("ble_idle",3600000L,81,76,false,false),
                trial("ble_idle",3600000L,82,77,false,false))).status ==
            BatteryDischargeStudy.Status.NOT_COMPARABLE, "charging rejected");
        check(BatteryDischargeStudy.compare(group(6),
            Arrays.asList(trial("ble_idle",3600000L,80,75,false,true),
                trial("ble_idle",3600000L,81,76,false,false),
                trial("ble_idle",3600000L,82,77,false,false))).status ==
            BatteryDischargeStudy.Status.NOT_COMPARABLE, "interruption rejected");
        check(BatteryDischargeStudy.compare(group(6),
            Arrays.asList(trial("ble_idle",3600000L,40,35,false,false),
                trial("ble_idle",3600000L,41,36,false,false),
                trial("ble_idle",3600000L,42,37,false,false))).status ==
            BatteryDischargeStudy.Status.NOT_COMPARABLE, "charge ranges must match");
        check(BatteryDischargeStudy.compare(group(6), group(1)).status ==
            BatteryDischargeStudy.Status.NOT_COMPARABLE, "1 percent delta unreliable");
        check(BatteryDischargeStudy.compare(null, group(6)).status ==
            BatteryDischargeStudy.Status.INSUFFICIENT_DATA, "missing group");
        System.out.println("PASS BatteryDischargeStudyTest (" + checks + " assertions; synthetic fixtures)");
    }
}
