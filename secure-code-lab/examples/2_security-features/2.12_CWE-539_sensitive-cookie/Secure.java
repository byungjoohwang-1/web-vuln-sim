import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;

/**
 * [안전 예제] 민감정보는 서버 세션에 보관 (CWE-539 / KISA 2.12)
 *
 * 인증 토큰 같은 민감정보는 브라우저 디스크에 남지 않도록 처리한다.
 *   1) 실제 값은 서버측 세션(getSession)에 저장한다.
 *   2) 클라이언트에는 식별자만 담되, 세션 쿠키(setMaxAge(0) 이하)로 만들어
 *      브라우저를 닫으면 사라지게 한다.
 *   3) HttpOnly/Secure 플래그로 스크립트 접근·평문 전송을 막는다.
 *
 * 안전 지점:
 *   - request.getSession(true) 에 민감 값 보관
 *   - cookie.setHttpOnly(true), cookie.setSecure(true)
 *   - cookie.setMaxAge(-1)  // 세션 쿠키(디스크 저장 안 함)
 */
public class Secure {

    /**
     * 민감정보는 세션에 넣고, 쿠키에는 식별자만 담아 세션 쿠키로 내려준다.
     */
    public Cookie issueSessionCookie(HttpServletRequest request, String authToken) {
        // ★ 안전: 민감한 실제 토큰은 서버 세션에 보관한다.
        HttpSession session = request.getSession(true);
        session.setAttribute("authToken", authToken);

        // 클라이언트에는 세션 식별용 값만 담는다.
        Cookie cookie = new Cookie("SID", session.getId());
        cookie.setPath("/");
        cookie.setHttpOnly(true); // 스크립트(JS)에서 쿠키 접근 차단
        cookie.setSecure(true);   // HTTPS 에서만 전송
        cookie.setMaxAge(-1);     // 세션 쿠키: 브라우저 종료 시 삭제(디스크 저장 안 함)
        return cookie;
    }

    public static void main(String[] args) {
        System.out.println("안전 예제: 민감정보는 세션에, 쿠키는 HttpOnly 세션 쿠키로.");
    }
}
