import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.util.Arrays;
import java.util.List;
import javax.servlet.http.HttpServletRequest;

/**
 * [안전 예제] CWE-918 SSRF 방어 (KISA 1.12)
 *
 * 목적지를 허용목록(ALLOWLIST)으로 제한한다.
 * 스킴(https)과 호스트를 검증하고, 허용된 호스트가 아니면 요청 자체를 거부한다.
 * 이렇게 하면 내부망/메타데이터 주소로의 우회 요청을 차단한다.
 */
public class Secure {

    // ✓ 안전: 서버가 접근을 허용하는 외부 호스트 화이트리스트
    private static final List<String> ALLOWLIST =
            Arrays.asList("api.partner.com", "images.example.com");

    private static boolean isAllowedHost(String host) {
        return host != null && ALLOWLIST.contains(host);
    }

    public String fetch(HttpServletRequest request) throws Exception {
        String raw = request.getParameter("target");

        // URI로 파싱해 스킴/호스트를 안전하게 추출한다.
        URI uri = new URI(raw);
        String scheme = uri.getScheme();
        String host = uri.getHost();

        // 스킴은 https만, 호스트는 허용목록만 통과
        if (scheme == null || !scheme.startsWith("https") || !isAllowedHost(host)) {
            throw new SecurityException("허용되지 않은 대상 URL: " + raw);
        }

        URL url = uri.toURL();
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
        return sb.toString();
    }

    public static void main(String[] args) {
        System.out.println("안전 예제: 허용목록 기반 SSRF 차단, 허용 호스트=" + ALLOWLIST);
    }
}
