import java.util.HashMap;
import java.util.Map;

/**
 * [취약 예제] 반복된 인증시도 제한 기능 부재 (CWE-307 / KISA 2.16)
 *
 * 로그인 실패 횟수를 세거나 계정을 잠그는 로직이 전혀 없다.
 * 공격자는 같은 계정에 대해 수천~수백만 번 비밀번호를 자동으로 시도(무차별 대입)해
 * 결국 올바른 비밀번호를 찾아낼 수 있다. 실패 지연·계정 잠금·CAPTCHA 등
 * 어떤 억제 장치도 없다.
 *
 * 위험 지점:
 *   public boolean login(...)  // 시도 횟수 제한/잠금 없음
 */
public class Vulnerable {

    /** 아이디 → 저장된 비밀번호(예시). 실제로는 해시로 저장한다. */
    private final Map<String, String> users = new HashMap<>();

    public Vulnerable() {
        users.put("alice", "correct-horse");
    }

    /**
     * 로그인 시도.
     * ★ 취약: 실패 횟수를 세지 않아 무한히 시도할 수 있다.
     */
    public boolean login(String username, String password) {
        String saved = users.get(username);
        // 실패해도 아무 제약이 없다. 몇 번을 틀리든 계속 시도 가능.
        return saved != null && saved.equals(password);
    }

    public static void main(String[] args) {
        Vulnerable v = new Vulnerable();
        // 무차별 대입: 제한이 없으니 계속 때려볼 수 있다.
        for (int i = 0; i < 1_000_000; i++) {
            if (v.login("alice", "guess-" + i)) {
                System.out.println("탈취 성공");
                break;
            }
        }
    }
}
