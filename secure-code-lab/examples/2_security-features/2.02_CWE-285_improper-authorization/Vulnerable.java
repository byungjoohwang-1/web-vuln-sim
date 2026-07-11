import java.util.HashMap;
import java.util.Map;

/**
 * [취약 예제] 부적절한 인가 (CWE-285 / KISA 2.2)
 *
 * 로그인은 되어 있지만, 요청한 자원이 "그 사용자의 것인지"를 확인하지 않는다.
 * 사용자가 계좌 식별자(accountId)만 바꿔 보내면 남의 계좌 정보를 조회할 수 있다.
 * (전형적인 IDOR / 수평적 권한 상승)
 *
 * 위험 지점:
 *   getParameter("accountId") 로 받은 식별자를 소유자 검증 없이 그대로 조회에 사용.
 */
public class Vulnerable {

    static class FakeRequest {
        Map<String, String> params = new HashMap<>();
        String getParameter(String k) { return params.get(k); }
    }

    /** accountId -> (소유자 loginId, 잔액) 데모 저장소. */
    static final Map<String, String> ACCOUNT_OWNER = new HashMap<>();
    static final Map<String, Long> ACCOUNT_BALANCE = new HashMap<>();
    static {
        ACCOUNT_OWNER.put("A-1001", "alice");
        ACCOUNT_OWNER.put("A-2002", "bob");
        ACCOUNT_BALANCE.put("A-1001", 500_000L);
        ACCOUNT_BALANCE.put("A-2002", 999_999L);
    }

    /**
     * ★ 취약: 요청 파라미터로 받은 accountId를 소유자 검증 없이 그대로 사용한다.
     *   alice로 로그인한 사용자가 accountId=A-2002 를 넣으면 bob의 잔액을 본다.
     */
    public long getBalance(FakeRequest request, String loginUser) {
        String accountId = request.getParameter("accountId"); // 외부 입력
        // 소유자 확인 없이 곧바로 조회 → 남의 자원 접근 가능
        return ACCOUNT_BALANCE.getOrDefault(accountId, 0L);
    }

    public static void main(String[] args) {
        FakeRequest req = new FakeRequest();
        req.params.put("accountId", "A-2002"); // 공격자는 남의 계좌 id를 넣는다
        // alice가 로그인했지만 bob(A-2002)의 잔액이 그대로 노출된다.
        System.out.println(new Vulnerable().getBalance(req, "alice"));
    }
}
