/**
 * [안전 예제] 강한 비밀번호 정책 강제 (CWE-521 / KISA 2.09)
 *
 * 최소 길이 8자 이상을 요구하고, 문자 종류 조합(대문자/소문자/숫자/특수문자)을
 * 정규식으로 강제한다. 또한 자주 유출되는 흔한 비밀번호는 차단한다.
 *
 * 안전 지점:
 *   - password.length() >= 8            // 충분한 최소 길이
 *   - password.matches(정규식)          // 복잡도(A-Z/a-z/0-9/특수문자) 강제
 *   - PASSWORD_POLICY 상수로 정책 명시
 */
import java.util.Set;

public class Secure {

    /** 정책을 코드로 명시해 리뷰·문서화가 쉽도록 한다. */
    static final String PASSWORD_POLICY =
            "최소 8자, 대문자/소문자/숫자/특수문자를 모두 포함";

    /** 흔히 유출되는 비밀번호 차단 목록(예시). 실제로는 외부 목록을 사용한다. */
    private static final Set<String> COMMON = Set.of(
            "password", "12345678", "qwerty12", "admin123");

    /**
     * 비밀번호가 정책을 만족하는지 검사한다.
     * ★ 안전: 길이 + 복잡도 + 흔한 비밀번호 차단을 모두 적용한다.
     */
    public boolean isAcceptable(String password) {
        if (password == null || password.length() >= 8 == false) {
            return false; // 8자 미만은 거부
        }
        if (COMMON.contains(password.toLowerCase())) {
            return false; // 사전에 오르는 흔한 값 거부
        }
        // 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개씩 요구한다.
        boolean complex = password.matches(
                "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^A-Za-z0-9]).{8,}$");
        return complex;
    }

    public static void main(String[] args) {
        Secure s = new Secure();
        System.out.println("정책: " + PASSWORD_POLICY);
        System.out.println("12345 허용? " + s.isAcceptable("12345"));       // false
        System.out.println("Str0ng!Pass 허용? " + s.isAcceptable("Str0ng!Pass")); // true
    }
}
