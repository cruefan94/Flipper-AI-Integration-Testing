package flipperai.battery;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

/** Cross-language fixture used only in public host CI, not real Bluetooth. */
public final class BatteryWireRoundTripTest {
    private BatteryWireRoundTripTest() {}
    public static void main(String[] args) throws Exception {
        if(args.length != 1) throw new IllegalArgumentException("request|response");
        if("request".equals(args[0])) {
            System.out.print(BatteryRequestCodec.encodeGet(7L));
            return;
        }
        if(!"response".equals(args[0]))
            throw new IllegalArgumentException("unknown mode");
        BufferedReader input = new BufferedReader(
            new InputStreamReader(System.in, StandardCharsets.UTF_8));
        String response = input.readLine();
        if(response == null) throw new AssertionError("no C response");
        BatteryOptimizer.Sample sample = BatteryTelemetryCodec.parseFrame(
            response + "\n", 1000L);
        if(sample.levelPct != 81 || sample.healthPct == null ||
           sample.healthPct.intValue() != 97 || sample.charging ||
           sample.activeHardwareTask)
            throw new AssertionError("C and Java wire fixtures disagree");
        System.err.println("PASS BatteryWireRoundTripTest (Java BAT_GET -> C -> Java BAT_TELEM)");
    }
}
