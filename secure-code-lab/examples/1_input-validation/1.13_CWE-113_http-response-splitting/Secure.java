import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * [안전 예제] CWE-113 HTTP 응답분할 방어 (KISA 1.13)
 *
 * 헤더 값에 넣기 전에 CR/LF(그리고 제어문자)를 제거한다.
 * CRLF가 사라지면 공격자가 헤더나 본문을 추가로 주입할 수 없다.
 * 화이트리스트 검증(matches)까지 병행하면 더 안전하다.
 */
public class Secure {

    /** stripCrlf : 개행문자(\r, \n)를 제거해 헤더 주입을 차단한다. */
    private static String stripCrlf(String value) {
        if (value == null) return "";
        // 캐리지리턴/라인피드 제거
        return value.replaceAll("[\\r\\n]", "");
    }

    public void setLang(HttpServletRequest request, HttpServletResponse response) {
        String lang = stripCrlf(request.getParameter("lang"));

        // ✓ 안전: 허용된 형식만 통과시키는 화이트리스트 검증
        if (!lang.matches("[a-zA-Z-]{2,10}")) {
            lang = "en";
        }
        response.addHeader("X-Preferred-Language", lang);

        // 리다이렉트 대상도 CRLF 제거 후 사용
        String next = stripCrlf(request.getParameter("next"));
        response.setHeader("Location", next);
    }

    public static void main(String[] args) {
        System.out.println("안전 예제: stripCrlf('ko\\r\\nSet-Cookie: x')='"
                + stripCrlf("ko\r\nSet-Cookie: x") + "'");
    }
}
