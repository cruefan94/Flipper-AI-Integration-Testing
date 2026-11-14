package flipperai.battery;

public final class BatteryTelemetryCodecTest {
    private static int assertions = 0;
    private static void check(boolean condition, String message) {
        assertions++;
        if(!condition) throw new AssertionError(message);
    }
    private static void reject(String frame) {
        boolean rejected = false;
        try { BatteryTelemetryCodec.parseFrame(frame, 400L); }
        catch(IllegalArgumentException expected) { rejected = true; }
        check(rejected, "should reject: " + frame.replace("\n", "\\n"));
    }
    public static void main(String[] args) {
        BatteryOptimizer.Sample sample = BatteryTelemetryCodec.parseFrame(
            "AI1|BAT_TELEM|7|v1,p=83,h=95,t=230,c=0,a=0\n", 1000L);
        check(sample.timestampMs == 1000L, "phone receive clock");
        check(sample.levelPct == 83, "level");
        check(sample.healthPct == 95, "health");
        check(sample.temperatureC == 23.0, "temperature");
        check(!sample.charging && !sample.activeHardwareTask, "status flags");
        BatteryOptimizer.Sample noExtra = BatteryTelemetryCodec.parseFrame(
            "AI1|BAT_TELEM|8|v1,p=2,c=1,a=1\n", 1000L);
        check(noExtra.healthPct == null && noExtra.temperatureC == null, "optional unknown");
        check(noExtra.activeHardwareTask && noExtra.charging, "active/charging");
        reject("AI1|ASK|7|v1,p=85,c=0,a=0\n");
        reject("AI1|BAT_TELEM|0|v1,p=85,c=0,a=0\n");
        reject("AI1|BAT_TELEM|4294967296|v1,p=85,c=0,a=0\n");
        reject("AI1|BAT_TELEM|7|v2,p=85,c=0,a=0\n");
        reject("AI1|BAT_TELEM|7|v1,p=101,c=0,a=0\n");
        reject("AI1|BAT_TELEM|7|v1,p=85,h=200,c=0,a=0\n");
        reject("AI1|BAT_TELEM|7|v1,p=85,t=1200,c=0,a=0\n");
        reject("AI1|BAT_TELEM|7|v1,p=85,c=1,a=2\n");
        reject("AI1|BAT_TELEM|7|v1,p=85,c=0\n");
        reject("AI1|BAT_TELEM|7|v1,p=85,p=84,c=0,a=0\n");
        reject("AI1|BAT_TELEM|7|v1,p=85,c=0,a=0\nBAD");
        reject("AI1|BAT_TELEM|7|v1,p=85,c=0,a=0|secret\n");
        reject("AI1|BAT_TELEM|7|v1,p=85,c=0,a=0");
        reject("AI1|BAT_TELEM|7|v1,p=85,c=0,a=0,\n");
        reject("AI1|BAT_TELEM|7|v1,p=85,c=0,a=0," + repeat("x",180) + "\n");
        System.out.println("PASS BatteryTelemetryCodecTest ("+assertions+" assertions; host-only)");
    }
    private static String repeat(String text, int n) {
        StringBuilder b = new StringBuilder();
        while(n-- > 0) b.append(text);
        return b.toString();
    }
}
