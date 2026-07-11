import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.regex.Pattern;

/**
 * [안전 예제] 운영체제 명령어 삽입 방어 (CWE-78 / KISA 4.5)
 *
 * 셸을 거치지 않는 ProcessBuilder 로 명령과 인자를 '배열'로 분리 전달한다.
 * 인자는 셸이 해석하지 않으므로 ; | && 메타문자가 무력화된다.
 * 추가로 입력값을 허용 패턴(allowlist)으로 검증한다.
 */
public class Secure {

    static String req(String name) {
        return "127.0.0.1";
    }

    // 허용 문자만 통과시키는 검증 (호스트/IP 형식만 허용)
    private static final Pattern HOST_ALLOWLIST = Pattern.compile("^[A-Za-z0-9.\\-]{1,253}$");

    public String ping() throws Exception {
        String host = req("host");

        if (!HOST_ALLOWLIST.matcher(host).matches()) {
            throw new IllegalArgumentException("허용되지 않은 호스트 형식: " + host);
        }

        // ★ 안전: ProcessBuilder 로 명령과 인자를 분리한다. 셸 해석이 없다.
        ProcessBuilder pb = new ProcessBuilder("ping", "-c", "1", host);
        pb.redirectErrorStream(true);
        Process p = pb.start();

        StringBuilder sb = new StringBuilder();
        try (BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()))) {
            String line;
            while ((line = r.readLine()) != null) {
                sb.append(line).append('\n');
            }
        }
        return sb.toString();
    }

    public static void main(String[] args) throws Exception {
        System.out.println(new Secure().ping());
    }
}
