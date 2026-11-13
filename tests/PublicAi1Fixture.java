// Public-only independent framing fixture. Not the production Android parser.
public final class PublicAi1Fixture {
    private PublicAi1Fixture() {}
    public static long requestId(byte[] frame) {
        if(frame == null || frame.length == 0 || frame.length > 256 || frame[frame.length - 1] != 10)
            throw new IllegalArgumentException("frame length or newline");
        for(byte b : frame) if(b == 0 || b == 13) throw new IllegalArgumentException("control");
        String s = new String(frame, java.nio.charset.StandardCharsets.UTF_8);
        if(!java.util.Arrays.equals(s.getBytes(java.nio.charset.StandardCharsets.UTF_8), frame))
            throw new IllegalArgumentException("utf8");
        String[] fields = s.substring(0, s.length()-1).split("\\|", 3);
        if(fields.length != 3 || fields[2].isEmpty() ||
           !java.util.Set.of("HELLO","ASK","ANSWER","ERROR").contains(fields[0]) ||
           !fields[1].matches("[0-9]{1,10}"))
            throw new IllegalArgumentException("fields");
        long id = Long.parseLong(fields[1]);
        if(id == 0 || id > 4294967295L) throw new IllegalArgumentException("id");
        return id;
    }
    public static void main(String[] args) {
        byte[][] valid = {"ASK|1|hi\n".getBytes(java.nio.charset.StandardCharsets.UTF_8),
                          "ASK|4294967295|café|more\n".getBytes(java.nio.charset.StandardCharsets.UTF_8)};
        for(byte[] b : valid) if(requestId(b) < 1) throw new AssertionError();
        String[] invalid = {"ASK|0|x\n","ASK|4294967296|x\n","ASK|1|\n","ASK|+1|x\n","ASK|1|x","OTHER|1|x\n"};
        for(String s : invalid) {
            boolean rejected = false;
            try {requestId(s.getBytes(java.nio.charset.StandardCharsets.UTF_8));}
            catch(IllegalArgumentException e) {rejected = true;}
            if(!rejected) throw new AssertionError("accepted invalid frame");
        }
        System.out.println("Public Java framing fixture passed");
    }
}
