/**
 * [취약 예제] 취약한 비밀번호 허용 (CWE-521 / KISA 2.09)
 *
 * 회원가입/비밀번호 변경 시 비밀번호 정책이 사실상 없다.
 * 아래 코드는 "4글자만 넘으면 통과"라는 매우 약한 길이 검사만 수행한다.
 * 길이·문자 종류(대문자/소문자/숫자/특수문자) 조합 요구가 전혀 없어
 * "1234", "aaaaa" 같은 사전 대입·무차별 대입에 즉시 뚫리는 값이 통과된다.
 *
 * 위험 지점:
 *   if (password.length() > 4)   // 정책이라 부르기 어려운 최소 길이 검사
 */
public class Vulnerable {

    /**
     * 비밀번호가 정책을 만족하는지 검사한다.
     * ★ 취약: 4자 초과이기만 하면 무엇이든 허용한다.
     *   - 복잡도(문자 종류 조합) 검사 없음
     *   - 흔한 비밀번호(1234, password 등) 차단 없음
     */
    public boolean isAcceptable(String password) {
        if (password == null) {
            return false;
        }
        // 최소 길이만 확인한다. 대소문자/숫자/특수문자 조합은 강제하지 않는다.
        if (password.length() > 4) {
            return true; // 예: "12345" 도 통과된다.
        }
        return false;
    }

    public static void main(String[] args) {
        Vulnerable v = new Vulnerable();
        // "12345" 처럼 위험한 값도 통과된다.
        System.out.println("12345 허용? " + v.isAcceptable("12345"));
        System.out.println("abcde 허용? " + v.isAcceptable("abcde"));
    }
}
