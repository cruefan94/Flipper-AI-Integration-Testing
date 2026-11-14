package flipperai.battery;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Locale;

/**
 * Offline utility to inspect recorded trials. The output is only provisional;
 * battery percentage is not a calibrated measurement of watt-hours.
 */
public final class BatteryTrialCli {
    private BatteryTrialCli() {}

    public static String analyze(String content) {
        BatteryTrialCsv.Groups groups = BatteryTrialCsv.parse(content);
        BatteryDischargeStudy.Result result = BatteryDischargeStudy.compare(
            groups.baseline, groups.candidate);
        if(result.status != BatteryDischargeStudy.Status.PROVISIONAL_COMPARISON)
            return "INCONCLUSIVE: " + result.limitation;
        return String.format(Locale.ROOT,
            "PROVISIONAL COMPARISON ONLY%n" +
            "Baseline discharge: %.3f percentage-points/hour%n" +
            "Candidate discharge: %.3f percentage-points/hour%n" +
            "Relative change: %.2f%% (positive means lower candidate discharge)%n" +
            "Limitations: %s%n",
            result.baselinePctPointsPerHour, result.candidatePctPointsPerHour,
            result.provisionalRateChangePct, result.limitation);
    }

    public static void main(String[] args) throws IOException {
        if(args.length != 1) {
            System.err.println("Usage: BatteryTrialCli trials.csv");
            System.exit(2);
        }
        Path path = Paths.get(args[0]);
        if(Files.size(path) > BatteryTrialCsv.MAX_BYTES)
            throw new IllegalArgumentException("CSV too large");
        String text = new String(Files.readAllBytes(path), StandardCharsets.UTF_8);
        System.out.println(analyze(text));
    }
}
