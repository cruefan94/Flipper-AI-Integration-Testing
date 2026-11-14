package flipperai.battery;

import java.util.Random;

/** Deterministic malformed-input stress; this is not formal fuzz coverage. */
public final class BatteryProtocolRobustnessTest {
    private BatteryProtocolRobustnessTest() {}
    public static void main(String[] args) {
        Random random = new Random(0x5EEDB47AL);
        int rejected = 0;
        for(int i = 0; i < 10000; i++) {
            int size = random.nextInt(260);
            StringBuilder candidate = new StringBuilder(size);
            for(int n = 0; n < size; n++) {
                int v = random.nextInt(160);
                candidate.append((char)v);
            }
            try {
                BatteryTelemetryCodec.parseFrame(candidate.toString(), 1000L);
                throw new AssertionError("Unexpectedly accepted randomized telemetry input");
            } catch(IllegalArgumentException expected) {
                rejected++;
            }
        }
        String valid = "AI1|BAT_TELEM|42|v1,p=70,h=95,t=-10,c=0,a=0\n";
        for(int at = 0; at < valid.length(); at++) {
            for(int bit = 0; bit < 7; bit++) {
                char[] chars = valid.toCharArray();
                chars[at] = (char)(chars[at] ^ (1 << bit));
                try {
                    BatteryTelemetryCodec.parseFrame(new String(chars), 1000L);
                    // A mutation can produce another syntactically valid frame.
                } catch(IllegalArgumentException expected) {
                    rejected++;
                }
            }
        }
        if(rejected < 10000) throw new AssertionError("Random corpus accepted invalid input");
        System.out.println("PASS BatteryProtocolRobustnessTest (" + rejected +
            " invalid frames rejected; deterministic corpus)");
    }
}
