import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/**
 * [취약 예제] 솔트 없이 일방향 해쉬 함수 사용 (CWE-759 / KISA 2.14)
 *
 * 비밀번호를 SHA-256으로 한 번 해싱만 하고 솔트를 사용하지 않는다.
 * 솔트가 없으면 같은 비밀번호는 항상 같은 해시가 되어,
 *   - 레인보우 테이블로 원문 역산이 쉽고
 *   - 여러 사용자의 동일 비밀번호가 한눈에 드러난다.
 * 또한 SHA-256은 빠른 해시라 무차별 대입에도 취약하다.
 *
 * 위험 지점:
 *   MessageDigest.getInstance("SHA-256")  // 솔트/반복(stretching) 없음
 */
public class Vulnerable {

    /**
     * 비밀번호를 저장용 해시로 변환한다.
     * ★ 취약: 솔트 없이 SHA-256 한 번만 적용한다.
     */
    public String hashPassword(String rawPassword) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] digest = md.digest(rawPassword.getBytes(StandardCharsets.UTF_8));

        StringBuilder sb = new StringBuilder();
        for (byte b : digest) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString(); // 같은 입력 → 항상 같은 출력(솔트 없음)
    }

    public static void main(String[] args) throws Exception {
        Vulnerable v = new Vulnerable();
        // 동일한 비밀번호는 언제나 동일한 해시가 된다(레인보우 테이블에 취약).
        System.out.println(v.hashPassword("hunter2"));
        System.out.println(v.hashPassword("hunter2"));
    }
}
