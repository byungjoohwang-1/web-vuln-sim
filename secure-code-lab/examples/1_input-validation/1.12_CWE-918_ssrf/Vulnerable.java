import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import javax.servlet.http.HttpServletRequest;

/**
 * [취약 예제] CWE-918 서버사이드 요청 위조 (KISA 1.12)
 *
 * 사용자가 지정한 URL로 서버가 직접 요청을 보낸다.
 * 목적지 검증이 없어 공격자는 내부망 주소(169.254.169.254, 127.0.0.1,
 * 내부 관리 API 등)를 지정해 서버를 프록시로 악용할 수 있다.
 */
public class Vulnerable {

    public String fetch(HttpServletRequest request) throws Exception {
        // ✗ 위험: 사용자 입력 URL을 그대로 신뢰 (danger: new URL(... getParameter)
        URL url = new URL(request.getParameter("target"));

        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");

        StringBuilder sb = new StringBuilder();
        try (BufferedReader br = new BufferedReader(
                new InputStreamReader(conn.getInputStream()))) {
            String line;
            while ((line = br.readLine()) != null) {
                sb.append(line);
            }
        }
        return sb.toString();   // 내부 메타데이터/관리 API 응답이 그대로 유출될 수 있음
    }

    public static void main(String[] args) {
        System.out.println("취약 예제: 사용자 지정 URL로 서버가 직접 요청");
    }
}
