import java.io.BufferedReader;
import java.io.InputStreamReader;

/**
 * [취약 예제] 운영체제 명령어 삽입 (CWE-78 / KISA 4.5)
 *
 * 외부 입력을 셸 명령 문자열에 그대로 이어 붙여 실행한다.
 * 공격자가 ; | && 같은 셸 메타문자를 넣으면 원래 명령 뒤에
 * 임의 명령을 덧붙여 실행할 수 있다.
 *
 * 위험 지점:
 *   Runtime.getRuntime().exec("ping " + host)
 */
public class Vulnerable {

    /** HTTP 요청 파라미터 흉내 헬퍼. */
    static String req(String name) {
        // 예: host = "127.0.0.1 && rm -rf /"
        return "127.0.0.1";
    }

    public String ping() throws Exception {
        String host = req("host"); // 신뢰할 수 없는 외부 입력

        // ★ 취약: 입력을 셸 명령 문자열에 직접 연결해 실행한다.
        //   host 에 "; cat /etc/passwd" 를 넣으면 추가 명령이 실행된다.
        Process p = Runtime.getRuntime().exec("ping -c 1 " + host);

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
        System.out.println(new Vulnerable().ping());
    }
}
