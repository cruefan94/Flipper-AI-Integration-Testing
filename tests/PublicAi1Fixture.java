// Independent public fixture matching Android SatelliteProtocol AI1 wire grammar.
// Production implementation lives in the Android repository, not here.
import java.nio.charset.StandardCharsets;
public final class PublicAi1Fixture {
    private PublicAi1Fixture() {}
    public static long requestId(byte[] frame) {
        if(frame == null || frame.length < 11 || frame.length > 180 || frame[frame.length - 1] != 10)
            throw new IllegalArgumentException("frame length or newline");
        String s = new String(frame, StandardCharsets.UTF_8);
        if(!java.util.Arrays.equals(s.getBytes(StandardCharsets.UTF_8), frame))
            throw new IllegalArgumentException("utf8");
        String[] fields = s.substring(0, s.length()-1).split("\\|", -1);
        if(fields.length != 4 || !fields[0].equals("AI1") ||
           !fields[1].matches("[A-Z_]{1,16}") || !fields[2].matches("[0-9]{1,10}"))
            throw new IllegalArgumentException("fields");
        for(int i=0;i<fields[3].length();i++) {
            char c = fields[3].charAt(i);
            if(c == '|' || c < 0x20 || c == 0x7f) throw new IllegalArgumentException("payload");
        }
        long id = Long.parseLong(fields[2]);
        if(id == 0 || id > 4294967295L) throw new IllegalArgumentException("id");
        return id;
    }
    public static void main(String[] args) {
        String[] valid = {"AI1|ASK|1|hi\n", "AI1|ASK|4294967295|café\n"};
        for(String s : valid) if(requestId(s.getBytes(StandardCharsets.UTF_8)) < 1) throw new AssertionError();
        String[] invalid = {"AI1|ASK|0|x\n","AI1|ASK|4294967296|x\n","AI1|ASK|+1|x\n",
            "AI1|ASK|1|x|y\n","AI1|ASK|1|x","OTHER|ASK|1|x\n","AI1|ASK|1|x\r\n"};
        for(String s : invalid) {
            boolean rejected = false;
            try {requestId(s.getBytes(StandardCharsets.UTF_8));}
            catch(IllegalArgumentException e) {rejected = true;}
            if(!rejected) throw new AssertionError("accepted invalid frame: " + s);
        }
        System.out.println("Public AI1 Java fixture passed");
    }
}
