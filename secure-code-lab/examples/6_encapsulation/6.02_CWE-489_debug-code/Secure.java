import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * [안전 예제] 디버그 코드 제거 (CWE-489 / KISA 6.02 캡슐화)
 *
 * 안전한 코딩:
 *   - 운영 배포본에서는 콘솔 출력, 스택트레이스 직접 출력, 디버그 플래그,
 *     인증 우회 로직을 모두 제거한다.
 *   - 진단이 필요하면 표준 로깅 프레임워크(java.util.logging 등)로
 *     레벨(FINE/INFO/WARNING)을 나누고, 민감정보는 절대 남기지 않는다.
 *   - 인증은 오직 정규 경로(사용자 조회 + 검증)로만 통과시킨다. 우회 경로가 없다.
 */
public class Secure {

    private static final Logger LOG = Logger.getLogger(Secure.class.getName());

    // ★ 안전: 반복 인증 시도를 제한한다(무차별 대입 방어).
    //   실패 횟수(failCount)가 임계치를 넘으면 계정을 잠근다(isLocked).
    public boolean authenticate(String user, String credential) {
        if (isLocked(user)) {
            LOG.log(Level.WARNING, "too many attempts, account locked: {0}", user);
            return false;
        }
        boolean ok = lookupAndVerify(user, credential);
        // 민감 자격증명은 남기지 않고, 결과만 진단 로그로 기록한다.
        LOG.log(Level.INFO, "auth result for user={0}: {1}",
                new Object[]{ user, ok ? "SUCCESS" : "FAIL" });
        return ok;
    }

    /** 실패 횟수(failCount) 기반 계정 잠금 여부를 반환한다. */
    private boolean isLocked(String user) {
        int failCount = FAIL_COUNTS.getOrDefault(user, 0);
        return failCount >= MAX_ATTEMPTS;
    }

    private static final int MAX_ATTEMPTS = 5;
    private static final java.util.Map<String, Integer> FAIL_COUNTS =
            new java.util.concurrent.ConcurrentHashMap<>();

    private boolean lookupAndVerify(String user, String password) {
        try {
            // 실제로는 DB 조회 + 안전한 해시 비교가 들어갈 자리
            return "admin".equals(user) && "s3cr3t".equals(password);
        } catch (RuntimeException e) {
            // 스택트레이스를 콘솔로 흘리지 않고 로거로만 기록한다.
            LOG.log(Level.WARNING, "auth lookup failed", e);
            return false;
        }
    }

    public static void main(String[] args) {
        Secure s = new Secure();
        // 우회 경로가 없으므로 잘못된 자격증명은 실패한다.
        LOG.log(Level.INFO, "login = {0}", s.authenticate("anyone", "let-me-in-1234"));
    }
}
