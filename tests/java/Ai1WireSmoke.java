import com.flipperai.satellite.SatelliteProtocol;
import java.nio.charset.StandardCharsets;

public final class Ai1WireSmoke {
  private static void eq(String a,String b) {if(!a.equals(b))throw new AssertionError(a+" != "+b);}
  private static void bad(String frame) {
    try {SatelliteProtocol.decode(frame);throw new AssertionError("accepted invalid frame");}
    catch(IllegalArgumentException expected){}
  }
  public static void main(String[] args) {
    eq(SatelliteProtocol.encode("PING",0,""),"AI1|PING|0|\n");
    eq(SatelliteProtocol.encode("ANSWER",4294967295L,"ready"),"AI1|ANSWER|4294967295|ready\n");
    String[] parts=SatelliteProtocol.decode("AI1|ASK|123|hello\n");
    eq(parts[1],"ASK");eq(parts[2],"123");eq(parts[3],"hello");
    bad("AI2|PING|1|hi\n");
    bad("AI1|bad|1|hi\n");
    bad("AI1|PING|1|a|b\n");
    bad("AI1|PING|1|hi\r\n");
    bad("AI1|PING|1|hi");
    try {SatelliteProtocol.encode("ANSWER",1,"é".repeat(90));throw new AssertionError("accepted oversize");}
    catch(IllegalArgumentException expected){}
    System.out.println("PASS: actual Android SatelliteProtocol Java framing smoke tests");
  }
}
