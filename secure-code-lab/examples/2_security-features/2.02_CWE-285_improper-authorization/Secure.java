import java.util.HashMap;
import java.util.Map;

/**
 * [안전 예제] 부적절한 인가 방지 (CWE-285 / KISA 2.2)
 *
 * 요청한 자원(계좌)이 현재 로그인한 사용자의 소유인지 서버에서 반드시 확인한다.
 * 소유자가 아니면 접근을 거부해 수평적 권한 상승(IDOR)을 막는다.
 *
 * 완화 지표:
 *   서버가 보관한 소유자(ownerId)와 로그인 사용자(loginUser)를 equals로 비교하고,
 *   isOwner 검증을 통과한 경우에만 자원을 반환한다.
 */
public class Secure {

    static class FakeRequest {
        Map<String, String> params = new HashMap<>();
        String getParameter(String k) { return params.get(k); }
    }

    static final Map<String, String> ACCOUNT_OWNER = new HashMap<>();
    static final Map<String, Long> ACCOUNT_BALANCE = new HashMap<>();
    static {
        ACCOUNT_OWNER.put("A-1001", "alice");
        ACCOUNT_OWNER.put("A-2002", "bob");
        ACCOUNT_BALANCE.put("A-1001", 500_000L);
        ACCOUNT_BALANCE.put("A-2002", 999_999L);
    }

    /** 서버가 보관한 소유자 정보로 소유 여부를 검증한다. */
    static boolean isOwner(String accountId, String loginUser) {
        String ownerId = ACCOUNT_OWNER.get(accountId); // 서버측 신뢰 데이터
        return ownerId != null && ownerId.equals(loginUser);
    }

    /**
     * ★ 안전: accountId가 로그인 사용자 소유인지 확인한 뒤에만 잔액을 반환한다.
     *   소유자가 아니면 예외로 거부한다.
     */
    public long getBalance(FakeRequest request, String loginUser) {
        String accountId = request.getParameter("accountId");
        if (!isOwner(accountId, loginUser)) {
            throw new SecurityException("접근 권한 없음: 본인 소유 자원이 아님");
        }
        return ACCOUNT_BALANCE.getOrDefault(accountId, 0L);
    }

    public static void main(String[] args) {
        FakeRequest req = new FakeRequest();
        req.params.put("accountId", "A-1001"); // 본인 계좌
        System.out.println(new Secure().getBalance(req, "alice"));
    }
}
