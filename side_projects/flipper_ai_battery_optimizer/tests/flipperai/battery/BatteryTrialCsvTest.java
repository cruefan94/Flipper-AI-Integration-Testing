package flipperai.battery;

public final class BatteryTrialCsvTest {
    private static int checks;
    private static void check(boolean ok, String message) {
        checks++;
        if(!ok) throw new AssertionError(message);
    }
    private static void reject(String text) {
        boolean failed = false;
        try { BatteryTrialCsv.parse(text); }
        catch(IllegalArgumentException expected) { failed = true; }
        check(failed, "invalid CSV should reject");
    }
    private static String sample() {
        StringBuilder sb = new StringBuilder(BatteryTrialCsv.HEADER).append('\n');
        for(int n = 0; n < 3; n++)
            sb.append("baseline,ble_idle,3600000,80,74,0,0\n");
        for(int n = 0; n < 3; n++)
            sb.append("candidate,ble_idle,3600000,80,75,0,0\n");
        return sb.toString();
    }
    public static void main(String[] args) {
        BatteryTrialCsv.Groups parsed = BatteryTrialCsv.parse(sample());
        check(parsed.baseline.size() == 3 && parsed.candidate.size() == 3,
            "group partition");
        check(BatteryTrialCli.analyze(sample()).contains("PROVISIONAL COMPARISON ONLY"),
            "tool never claims proven improvement");
        boolean immutable = false;
        try { parsed.baseline.clear(); }
        catch(UnsupportedOperationException expected) { immutable = true; }
        check(immutable, "return immutable groups");

        reject(null);
        reject("");
        reject("group,invalid\n");
        reject(BatteryTrialCsv.HEADER + "\nunknown,ble_idle,3600000,80,75,0,0\n");
        reject(BatteryTrialCsv.HEADER + "\nbaseline,ble_idle,-10,80,75,0,0\n");
        reject(BatteryTrialCsv.HEADER + "\nbaseline,ble_idle,3600000,101,75,0,0\n");
        reject(BatteryTrialCsv.HEADER + "\nbaseline,ble_idle,3600000,80,75,1,2\n");
        reject(BatteryTrialCsv.HEADER + "\nbaseline,ble idle,3600000,80,75,0,0\n");
        reject(BatteryTrialCsv.HEADER + "\nbaseline,ble_idle,3600000,80,75,0\n");
        reject(BatteryTrialCsv.HEADER + "\nbaseline,ble_idle,3600000,80,75,0,0\n\n");
        StringBuilder excessive = new StringBuilder(BatteryTrialCsv.HEADER).append('\n');
        for(int i=0;i<201;i++)
            excessive.append("baseline,ble_idle,3600000,80,75,0,0\n");
        reject(excessive.toString());

        String insufficient = BatteryTrialCsv.HEADER +
            "\nbaseline,ble_idle,3600000,80,74,0,0\n";
        check(BatteryTrialCli.analyze(insufficient).startsWith("INCONCLUSIVE"),
            "too few trials rejected");
        System.out.println("PASS BatteryTrialCsvTest (" + checks + " assertions)");
    }
}
