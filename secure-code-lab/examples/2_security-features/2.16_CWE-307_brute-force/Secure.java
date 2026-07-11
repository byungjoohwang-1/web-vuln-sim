import java.time.Duration;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

/**
 * [안전 예제] 반복 인증시도 제한 (CWE-307 / KISA 2.16)
 *
 * 계정별 로그인 실패 횟수(failCount)를 세고, 임계치를 넘으면 일정 시간 잠근다.
 *   - 연속 실패가 임계치에 도달하면 isLocked 상태로 전환한다.
 *   - 잠금 시간 동안은 올바른 비밀번호라도 즉시 거부한다.
 *   - 성공 시 카운터를 초기화한다.
 * (운영에서는 IP 기준 RateLimiter, 지수 지연, CAPTCHA 등을 함께 쓴다.)
 *
 * 안전 지점:
 *   - failCount 로 실패 시도 누적
 *   - isLocked() 로 잠금 여부 확인
 */
public class Secure {

    private static final int MAX_ATTEMPTS = 5;
    private static final Duration LOCK_TIME = Duration.ofMinutes(15);

    private final Map<String, String> users = new HashMap<>();
    private final Map<String, Integer> failCount = new HashMap<>();
    private final Map<String, Instant> lockedUntil = new HashMap<>();

    public Secure() {
        users.put("alice", "correct-horse");
    }

    /** 현재 계정이 잠금 상태인지 확인한다. */
    public boolean isLocked(String username) {
        Instant until = lockedUntil.get(username);
        return until != null && Instant.now().isBefore(until);
    }

    /**
     * 로그인 시도.
     * ★ 안전: 잠금 확인 → 검증 → 실패 누적/잠금 처리 순으로 동작한다.
     */
    public boolean login(String username, String password) {
        if (isLocked(username)) {
            // 너무 많은 실패(tooMany)로 잠긴 계정은 즉시 거부한다.
            return false;
        }

        String saved = users.get(username);
        boolean ok = saved != null && saved.equals(password);

        if (ok) {
            failCount.remove(username); // 성공 시 실패 카운터 초기화
            lockedUntil.remove(username);
            return true;
        }

        // 실패 횟수를 누적하고, 임계치 도달 시 계정을 잠근다.
        int attempts = failCount.merge(username, 1, Integer::sum);
        if (attempts >= MAX_ATTEMPTS) {
            lockedUntil.put(username, Instant.now().plus(LOCK_TIME));
        }
        return false;
    }

    public static void main(String[] args) {
        Secure s = new Secure();
        for (int i = 0; i < 10; i++) {
            boolean ok = s.login("alice", "wrong");
            System.out.println("시도 " + (i + 1) + " 성공?" + ok + " 잠금?" + s.isLocked("alice"));
        }
    }
}
