/**
 * [취약 예제] 제거되지 않고 남은 디버그 코드 (CWE-489 / KISA 6.02 캡슐화)
 *
 * 개념:
 *   개발 중 편의를 위해 넣은 디버그 출력, 디버그 플래그, 우회(백도어) 로직이
 *   운영 배포본에 그대로 남으면 공격 표면이 된다.
 *
 * 위험 지점:
 *   - boolean DEBUG = true 로 켜진 디버그 모드
 *   - System.out.println / printStackTrace 로 내부 상태·스택트레이스 노출
 *   - "마스터 비밀번호(master password)" 백도어로 인증 우회
 */
public class Vulnerable {

    // ★ 취약: 운영에 남은 디버그 플래그
    boolean DEBUG = true;

    // ★ 취약: 개발자 백도어 — 이 값이면 무조건 로그인 성공
    private static final String MASTER_PASSWORD = "let-me-in-1234"; // master password backdoor

    public boolean authenticate(String user, String password) {
        // ★ 취약: 마스터 비밀번호(master password) 백도어로 인증 우회
        if (MASTER_PASSWORD.equals(password)) {
            return true;
        }

        boolean ok = lookupAndVerify(user, password);

        // ★ 취약: 디버그 모드에서 민감정보를 콘솔에 그대로 출력
        if (debug) {
            System.out.println("[DEBUG] user=" + user + " pw=" + password + " ok=" + ok);
        }
        return ok;
    }

    private final boolean debug = true;

    private boolean lookupAndVerify(String user, String password) {
        try {
            // 실제로는 DB 조회/해시 비교가 들어갈 자리
            return "admin".equals(user) && "s3cr3t".equals(password);
        } catch (Exception e) {
            // ★ 취약: 스택트레이스를 그대로 노출
            e.printStackTrace();
            return false;
        }
    }

    public static void main(String[] args) {
        Vulnerable v = new Vulnerable();
        // 백도어로 로그인 성공
        System.out.println("backdoor login = " + v.authenticate("anyone", "let-me-in-1234"));
    }
}
