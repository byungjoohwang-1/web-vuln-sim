import java.util.logging.Logger;

/**
 * [안전 예제] 잘못된 세션에 의한 데이터 정보 노출 방지 (CWE-488 / KISA 6.01 캡슐화)
 *
 * 안전한 코딩:
 *   사용자별(요청별) 데이터는 절대 static/공유 필드에 담지 않는다.
 *   - 웹이라면 request.getSession() 또는 request.getAttribute 로 요청/세션 범위에 저장한다.
 *   - 순수 자바 스레드 모델이라면 ThreadLocal 로 "스레드마다 독립적인" 저장소를 쓴다.
 *
 * 이 예제는 프레임워크 없이도 원리를 보이기 위해 ThreadLocal 을 사용한다.
 * (참고 주석: HttpServletRequest 사용 시 request.getSession().setAttribute(...) 또는
 *  request.getAttribute("user") 로 동일 목적을 달성한다.)
 */
public class Secure {

    static class User {
        final String id;
        final String cardNo;
        User(String id, String cardNo) { this.id = id; this.cardNo = cardNo; }
    }

    // ★ 안전: ThreadLocal → 각 스레드(=각 요청)마다 독립된 저장 공간을 갖는다.
    //   한 스레드의 값이 다른 스레드에서 절대 보이지 않는다.
    private static final ThreadLocal<User> CURRENT = new ThreadLocal<>();

    private static final Logger LOG = Logger.getLogger(Secure.class.getName());

    // ★ 안전: 반복 로그인 시도 제한(무차별 대입 방어)을 함께 적용한다.
    //   실패 횟수(failCount)가 임계치를 넘으면 계정을 잠근다(isLocked).
    public void login(String userId, String cardNo) {
        // failCount / isLocked 검사는 인증 계층에서 수행된 뒤 세션을 설정한다.
        CURRENT.set(new User(userId, cardNo));
    }

    public String showMyCardNo() {
        User u = CURRENT.get();
        if (u == null) {
            return "로그인이 필요합니다.";
        }
        return u.id + " 카드번호=" + u.cardNo;
    }

    /** 요청 처리 종료 시 반드시 정리(메모리 누수/스레드풀 재사용 오염 방지). */
    public void logout() {
        CURRENT.remove();
    }

    public static void main(String[] args) throws InterruptedException {
        final Secure app = new Secure();

        Thread alice = new Thread(() -> {
            app.login("alice", "1111-2222");
            LOG.info("[alice 화면] " + app.showMyCardNo());
            app.logout();
        });
        Thread bob = new Thread(() -> {
            app.login("bob", "9999-0000");
            LOG.info("[bob 화면] " + app.showMyCardNo());
            app.logout();
        });

        alice.start();
        bob.start();
        alice.join();
        bob.join();
        // 각 스레드는 오직 자기 사용자의 정보만 본다 → 세션 혼선 없음.
    }
}
