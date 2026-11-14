package flipperai.battery;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Read-only A/B study helper. A percentage-point discharge estimate is NOT a
 * power measurement or a scientific proof of battery-life improvement.
 *
 * Trial metadata and measurements are supplied by a test operator. No BLE,
 * device mutations, analytics upload, or background sampling is implemented.
 */
public final class BatteryDischargeStudy {
    private BatteryDischargeStudy() {}

    public enum Status { INSUFFICIENT_DATA, NOT_COMPARABLE, PROVISIONAL_COMPARISON }

    public static final class Trial {
        public final String workload;
        public final long durationMs;
        public final int startBatteryPct;
        public final int endBatteryPct;
        public final boolean chargingObserved;
        public final boolean interrupted;

        public Trial(String workload, long durationMs, int startBatteryPct,
                     int endBatteryPct, boolean chargingObserved, boolean interrupted) {
            this.workload = workload;
            this.durationMs = durationMs;
            this.startBatteryPct = startBatteryPct;
            this.endBatteryPct = endBatteryPct;
            this.chargingObserved = chargingObserved;
            this.interrupted = interrupted;
        }
    }

    public static final class Result {
        public final Status status;
        public final double baselinePctPointsPerHour;
        public final double candidatePctPointsPerHour;
        /** Positive indicates lower measured discharge rate in the candidate group. */
        public final double provisionalRateChangePct;
        public final String limitation;

        private Result(Status status, double baseline, double candidate,
                       double rateChange, String limitation) {
            this.status = status;
            this.baselinePctPointsPerHour = baseline;
            this.candidatePctPointsPerHour = candidate;
            this.provisionalRateChangePct = rateChange;
            this.limitation = limitation;
        }
    }

    private static Result inconclusive(Status status, String message) {
        return new Result(status, Double.NaN, Double.NaN, Double.NaN, message);
    }

    private static boolean validTrial(Trial trial) {
        if(trial == null || trial.workload == null ||
           !trial.workload.matches("[A-Za-z0-9_\\-]{1,40}") ||
           trial.durationMs < 1800000L || trial.durationMs > 43200000L ||
           trial.startBatteryPct < 0 || trial.startBatteryPct > 100 ||
           trial.endBatteryPct < 0 || trial.endBatteryPct > 100 ||
           trial.chargingObserved || trial.interrupted)
            return false;
        int delta = trial.startBatteryPct - trial.endBatteryPct;
        return delta >= 2 && delta <= 50;
    }

    private static double medianRate(List<Trial> trials) {
        ArrayList<Double> rates = new ArrayList<Double>();
        for(Trial trial : trials) {
            double rate = ((trial.startBatteryPct - trial.endBatteryPct) * 3600000.0)
                         / trial.durationMs;
            rates.add(rate);
        }
        Collections.sort(rates);
        int half = rates.size() / 2;
        if((rates.size() & 1) == 1) return rates.get(half);
        return (rates.get(half-1) + rates.get(half)) / 2.0;
    }

    /**
     * Require >=3 controlled trials in each arm using identical workload labels
     * and starting charge ranges within 10 percentage points. Temperature,
     * background activity and battery age are NOT measured; comparison stays
     * provisional even when nominal controls match.
     */
    public static Result compare(List<Trial> baseline, List<Trial> candidate) {
        if(baseline == null || candidate == null ||
           baseline.size() < 3 || candidate.size() < 3)
            return inconclusive(Status.INSUFFICIENT_DATA, "At least three valid trials per group are needed.");
        String workload = null;
        int minStart = 101;
        int maxStart = -1;
        for(List<Trial> group : new List[]{baseline, candidate}) {
            for(Trial trial : group) {
                if(!validTrial(trial))
                    return inconclusive(Status.NOT_COMPARABLE,
                        "Charging, interruptions, insufficient discharge, or invalid trial data.");
                if(workload == null) workload = trial.workload;
                if(!workload.equals(trial.workload))
                    return inconclusive(Status.NOT_COMPARABLE, "Different workload types.");
                minStart = Math.min(minStart, trial.startBatteryPct);
                maxStart = Math.max(maxStart, trial.startBatteryPct);
            }
        }
        if(maxStart - minStart > 10)
            return inconclusive(Status.NOT_COMPARABLE, "Starting battery levels differ too much.");
        double baseRate = medianRate(baseline);
        double candidateRate = medianRate(candidate);
        double relativeChange = 100.0 * (baseRate - candidateRate) / baseRate;
        return new Result(Status.PROVISIONAL_COMPARISON, baseRate, candidateRate,
            relativeChange,
            "Preliminary percent-point comparison only. No direct watt-hour data, " +
            "temperature controls or statistical confidence; repeat physical tests.");
    }
}
