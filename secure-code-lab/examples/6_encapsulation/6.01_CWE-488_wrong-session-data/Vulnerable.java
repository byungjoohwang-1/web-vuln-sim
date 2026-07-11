/**
 * [취약 예제] 잘못된 세션에 의한 데이터 정보 노출 (CWE-488 / KISA 6.01 캡슐화)
 *
 * 개념:
 *   웹/서버 애플리케이션은 여러 사용자의 요청을 동시에 처리한다.
 *   보통 서블릿/컨트롤러 인스턴스는 여러 스레드가 공유하므로,
 *   사용자별(=요청별) 데이터를 "인스턴스 필드"나 "static 필드"에 담으면
 *   한 사용자의 데이터가 다른 사용자의 요청에서 그대로 보인다.
 *
 * 위험 지점:
 *   private static 필드(currentUser)에 로그인한 사용자를 보관한다.
 *   static 은 클래스당 단 하나이므로, 모든 요청·모든 스레드가 이 값을 공유한다.
 *   A 사용자가 로그인한 직후 B 사용자의 요청이 들어오면,
 *   B 는 A 의 계정 정보를 그대로 조회하게 된다(세션 혼선).
 */
public class Vulnerable {

    // 사용자 한 명을 표현하는 단순 모델
    static class User {
        final String id;
        final String cardNo; // 민감정보 예시
        User(String id, String cardNo) { this.id = id; this.cardNo = cardNo; }
    }

    // ★ 취약: 사용자별 상태를 static 필드에 저장한다.
    //   서버 전체에서 단 하나만 존재하므로 모든 요청이 이 값을 덮어쓰고 공유한다.
    private static User currentUser;

    /** 로그인 처리: 세션이 아니라 static 필드에 사용자를 심는다(위험). */
    public void login(String userId, String cardNo) {
        currentUser = new User(userId, cardNo);
    }

    /** "현재 사용자"의 카드번호를 반환 → 실제로는 마지막으로 로그인한 아무나의 값 */
    public String showMyCardNo() {
        if (currentUser == null) {
            return "로그인이 필요합니다.";
        }
        // ★ 다른 사용자의 요청 스레드에서도 이 static 값을 그대로 읽는다 → 정보 노출
        return currentUser.id + " 카드번호=" + currentUser.cardNo;
    }

    public static void main(String[] args) throws InterruptedException {
        final Vulnerable app = new Vulnerable();

        // 사용자 A 로그인
        Thread a = new Thread(() -> app.login("alice", "1111-2222"));
        // 사용자 B 로그인
        Thread b = new Thread(() -> app.login("bob", "9999-0000"));
        a.start(); a.join();
        b.start(); b.join();

        // alice 가 자기 정보를 보려 하지만, static 필드는 마지막에 로그인한 bob 로 덮여있다.
        System.out.println("[alice 화면] " + app.showMyCardNo());
    }
}
