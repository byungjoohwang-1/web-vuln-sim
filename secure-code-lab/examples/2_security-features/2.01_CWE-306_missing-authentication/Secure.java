import java.util.HashMap;
import java.util.Map;

/**
 * [안전 예제] 적절한 인증 없는 중요기능 허용 방지 (CWE-306 / KISA 2.1)
 *
 * 중요기능을 실행하기 전에 서버 세션에서 로그인/권한을 먼저 확인한다.
 * 인증되지 않았거나 권한이 없으면 기능을 수행하지 않고 즉시 거부한다.
 *
 * 완화 지표:
 *   getSession(false) 로 기존 세션만 조회하고,
 *   getAttribute("user") / getAttribute("login") 로 인증 상태를 확인한다.
 */
public class Secure {

    static class FakeSession {
        Map<String, Object> attrs = new HashMap<>();
        Object getAttribute(String k) { return attrs.get(k); }
    }
    static class FakeRequest {
        FakeSession session;
        FakeRequest(FakeSession s) { this.session = s; }
        String getParameter(String k) { return "1000"; }
        // getSession(false): 로그인으로 만들어진 세션이 없으면 null을 돌려준다.
        FakeSession getSession(boolean create) { return session; }
    }
    static class FakeResponse {
        int status = 200;
        void sendError(int code) { this.status = code; }
        void write(String s) { System.out.println(s); }
    }

    static final Map<String, Integer> POINTS = new HashMap<>();

    /**
     * ★ 안전: 중요기능 실행 전에 서버 세션으로 인증을 확인한다.
     *   - getSession(false): 이미 로그인된 세션만 가져온다(없으면 null).
     *   - getAttribute("user"): 로그인 시 저장해 둔 사용자 정보로 인증 확인.
     *   - 권한("role")이 관리자인지까지 확인한다.
     */
    public void doPost(FakeRequest request, FakeResponse response) {
        FakeSession session = request.getSession(false);
        Object user = (session == null) ? null : session.getAttribute("user");
        // ★ 안전: 권한("role")은 반드시 서버 세션에서만 읽는다(요청 파라미터 신뢰 금지).
        //   server-side 값이므로 클라이언트가 위조할 수 없다.
        Object role = (session == null) ? null : session.getAttribute("role");

        // ★ 안전: CSRF 토큰을 서버 세션 값과 대조해 위조 요청을 차단한다.
        //   (쿠키에는 SameSite=Strict 를 함께 적용한다.)
        Object csrfInSession = (session == null) ? null : session.getAttribute("csrfToken");
        String csrfInForm = request.getParameter("csrfToken");
        if (csrfInSession == null || !csrfInSession.equals(csrfInForm)) {
            response.sendError(403); // CSRF 검증 실패 → 거부
            return;
        }

        if (user == null) {
            response.sendError(401); // 미인증 → 거부
            return;
        }
        if (!"ADMIN".equals(role)) {
            response.sendError(403); // 권한 없음 → 거부
            return;
        }

        int amount = Integer.parseInt(request.getParameter("amount"));
        POINTS.put("member-a", POINTS.getOrDefault("member-a", 0) + amount);
        POINTS.put("member-b", POINTS.getOrDefault("member-b", 0) + amount);
        response.write("관리자(" + user + ") 확인 후 " + amount + "포인트 지급 완료");
    }

    public static void main(String[] args) {
        FakeSession s = new FakeSession();
        s.attrs.put("user", "admin01");
        s.attrs.put("role", "ADMIN");
        new Secure().doPost(new FakeRequest(s), new FakeResponse());
    }
}
