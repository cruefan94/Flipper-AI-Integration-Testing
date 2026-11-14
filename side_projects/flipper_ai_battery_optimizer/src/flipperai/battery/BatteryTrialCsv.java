package flipperai.battery;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Local-only strict CSV import for manually recorded battery trials.
 * No network, BLE or automatic monitoring; no private identifiers in schema.
 */
public final class BatteryTrialCsv {
    private BatteryTrialCsv() {}
    public static final String HEADER =
        "group,workload,duration_ms,start_pct,end_pct,charging,interrupted";
    public static final int MAX_BYTES = 65536;

    public static final class Groups {
        public final List<BatteryDischargeStudy.Trial> baseline;
        public final List<BatteryDischargeStudy.Trial> candidate;
        private Groups(List<BatteryDischargeStudy.Trial> base,
                       List<BatteryDischargeStudy.Trial> modified) {
            baseline = Collections.unmodifiableList(base);
            candidate = Collections.unmodifiableList(modified);
        }
    }

    public static Groups parse(String text) {
        if(text == null || text.length() == 0 || text.length() > MAX_BYTES)
            throw new IllegalArgumentException("CSV empty or too large");
        String[] lines = text.split("\n", -1);
        if(lines.length < 2 || !HEADER.equals(lines[0].replace("\r", "")))
            throw new IllegalArgumentException("incorrect CSV schema");
        ArrayList<BatteryDischargeStudy.Trial> base =
            new ArrayList<BatteryDischargeStudy.Trial>();
        ArrayList<BatteryDischargeStudy.Trial> modified =
            new ArrayList<BatteryDischargeStudy.Trial>();
        int count = 0;
        for(int row = 1; row < lines.length; row++) {
            String line = lines[row].replace("\r", "");
            if(line.isEmpty() && row == lines.length - 1) continue;
            if(line.isEmpty()) throw new IllegalArgumentException("empty row");
            if(++count > 200) throw new IllegalArgumentException("too many trials");
            String[] parts = line.split(",", -1);
            if(parts.length != 7) throw new IllegalArgumentException("invalid row columns");
            if(!parts[1].matches("[A-Za-z0-9_-]{1,40}"))
                throw new IllegalArgumentException("invalid workload");
            long duration = parseUnsignedLong(parts[2]);
            int start = parsePercent(parts[3]);
            int end = parsePercent(parts[4]);
            boolean charging = parseBit(parts[5]);
            boolean interrupted = parseBit(parts[6]);
            BatteryDischargeStudy.Trial trial = new BatteryDischargeStudy.Trial(
                parts[1], duration, start, end, charging, interrupted);
            if("baseline".equals(parts[0])) base.add(trial);
            else if("candidate".equals(parts[0])) modified.add(trial);
            else throw new IllegalArgumentException("invalid group");
        }
        return new Groups(base, modified);
    }

    private static long parseUnsignedLong(String text) {
        if(!text.matches("[0-9]{1,14}"))
            throw new IllegalArgumentException("invalid duration");
        return Long.parseLong(text);
    }

    private static int parsePercent(String text) {
        if(!text.matches("[0-9]{1,3}"))
            throw new IllegalArgumentException("invalid battery percent");
        int value = Integer.parseInt(text);
        if(value > 100) throw new IllegalArgumentException("out-of-range percent");
        return value;
    }

    private static boolean parseBit(String text) {
        if("0".equals(text)) return false;
        if("1".equals(text)) return true;
        throw new IllegalArgumentException("invalid boolean");
    }
}
