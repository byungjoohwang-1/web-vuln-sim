import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * [취약 예제] CWE-113 HTTP 응답분할 (KISA 1.13)
 *
 * 사용자 입력을 응답 헤더 값에 그대로 넣는다.
 * 입력에 CR(\r), LF(\n)가 포함되면 헤더가 조기에 끝나고 공격자가
 * 새 헤더나 본문(2차 응답)을 주입해 캐시 오염·XSS로 이어질 수 있다.
 */
public class Vulnerable {

    public void setLang(HttpServletRequest request, HttpServletResponse response) {
        // ✗ 위험: 사용자 입력을 헤더 값에 그대로 사용 (danger: addHeader(... getParameter)
        response.addHeader("X-Preferred-Language", request.getParameter("lang"));

        // 리다이렉트 URL도 마찬가지로 CRLF 주입에 노출된다.
        response.setHeader("Location", request.getParameter("next"));
    }

    public static void main(String[] args) {
        System.out.println("취약 예제: CRLF 필터 없이 헤더에 사용자 입력 주입");
    }
}
