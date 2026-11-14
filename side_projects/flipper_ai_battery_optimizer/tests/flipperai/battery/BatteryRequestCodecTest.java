package flipperai.battery;

public final class BatteryRequestCodecTest {
    private static int assertions;
    private static void check(boolean ok, String desc) {
        assertions++;
        if(!ok) throw new AssertionError(desc);
    }
    private static void reject(long id) {
        boolean blocked = false;
        try { BatteryRequestCodec.encodeGet(id); }
        catch(IllegalArgumentException expected) { blocked = true; }
        check(blocked, "bad ID must reject " + id);
    }
    public static void main(String[] args) {
        check("AI1|BAT_GET|7|v1\n".equals(BatteryRequestCodec.encodeGet(7)), "canonical request");
        check("AI1|BAT_GET|4294967295|v1\n".equals(
            BatteryRequestCodec.encodeGet(4294967295L)), "maximum ID");
        reject(0);
        reject(-1);
        reject(0x100000000L);
        check(BatteryRequestCodec.encodeGet(123).endsWith("\n"), "single terminal LF");
        System.out.println("PASS BatteryRequestCodecTest (" + assertions +
            " assertions; no BLE/network writes)");
    }
}
