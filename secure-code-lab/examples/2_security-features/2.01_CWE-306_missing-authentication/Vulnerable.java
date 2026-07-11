import java.util.HashMap;
import java.util.Map;

/**
 * [취약 예제] 적절한 인증 없는 중요기능 허용 (CWE-306 / KISA 2.1)
 *
 * 관리자만 실행해야 하는 "전 회원 포인트 지급" 같은 중요기능을
 * 로그인/세션 확인 없이 곧바로 실행한다.
 * 공격자가 엔드포인트 URL만 알면 인증 절차 없이 기능을 호출할 수 있다.
 *
 * 위험 지점:
 *   doPost() 진입 직후 어떤 세션/권한 검사도 없이 곧바로 관리 기능을 수행한다.
 */
public class Vulnerable {

    /** 서블릿 요청/세션을 흉내내는 아주 작은 헬퍼들 (실제로는 HttpServletRequest). */
    static class FakeSession {
        Map<String, Object> attrs = new HashMap<>();
        Object getAttribute(String k) { return attrs.get(k); }
    }
    static class FakeRequest {
        FakeSession session = new FakeSession();
        String getParameter(String k) { return "1000"; }
        // 세션 조회 헬퍼(데모용). 취약 코드는 이 세션을 아예 확인하지 않는다.
        FakeSession lookupSession(boolean create) { return session; }
    }
    static class FakeResponse {
        void write(String s) { System.out.println(s); }
    }

    /** 데모용 회원 포인트 저장소. */
    static final Map<String, Integer> POINTS = new HashMap<>();

    /**
     * 중요기능: 모든 회원에게 포인트를 지급한다(관리자 전용이어야 함).
     *
     * ★ 취약: doPost 진입 직후 인증/권한 확인이 전혀 없다.
     *   누구든 이 요청을 보내면 관리 기능이 그대로 실행된다.
     */
    public void doPost(FakeRequest request, FakeResponse response) {
        int amount = Integer.parseInt(request.getParameter("amount"));

        // 세션 확인, 로그인 확인, 권한 확인 없이 곧바로 중요기능 수행
        POINTS.put("member-a", POINTS.getOrDefault("member-a", 0) + amount);
        POINTS.put("member-b", POINTS.getOrDefault("member-b", 0) + amount);

        response.write("모든 회원에게 " + amount + "포인트 지급 완료");
    }

    public static void main(String[] args) {
        new Vulnerable().doPost(new FakeRequest(), new FakeResponse());
    }
}
