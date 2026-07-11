import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * [안전 예제] CWE-352 CSRF 방어 (KISA 1.11)
 *
 * 동기화 토큰 패턴(Synchronizer Token Pattern)을 사용한다.
 * 서버는 세션에 예측 불가능한 CSRF 토큰을 저장하고, 폼에 숨겨서 내려보낸다.
 * 상태변경 요청이 오면 파라미터로 온 토큰과 세션의 토큰을 비교한다.
 * 추가로 쿠키에 SameSite 속성을 적용한다.
 */
public class Secure extends HttpServlet {

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws java.io.IOException {

        // ✓ 안전: 세션에 보관된 CSRF 토큰과 요청 토큰을 비교한다.
        String sessionToken = (String) request.getSession().getAttribute("csrfToken");
        String formToken = request.getParameter("_token");   // 폼 hidden 필드

        if (sessionToken == null || !sessionToken.equals(formToken)) {
            // 토큰 불일치 → 위조 요청으로 판단하고 거부
            response.sendError(HttpServletResponse.SC_FORBIDDEN, "CSRF token mismatch");
            return;
        }

        // 세션 쿠키에는 SameSite=Strict 적용을 권장 (아래는 설명용 헤더 예시)
        response.setHeader("Set-Cookie", "JSESSIONID=...; HttpOnly; Secure; SameSite=Strict");

        String to = request.getParameter("to");
        String amount = request.getParameter("amount");
        Object user = request.getSession().getAttribute("loginUser");
        if (user != null) {
            transfer(user.toString(), to, amount);
            response.getWriter().write("transfer done");
        }
    }

    private void transfer(String from, String to, String amount) {
        System.out.println(from + " -> " + to + " : " + amount);
    }

    public static void main(String[] args) {
        System.out.println("안전 예제: CSRF 토큰 검증 + SameSite 쿠키");
    }
}
