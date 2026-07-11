import java.security.SecureRandom;
import java.security.spec.KeySpec;
import java.util.Base64;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

/**
 * [안전 예제] 솔트 + 키 스트레칭 해시 (CWE-759 / KISA 2.14)
 *
 * 비밀번호마다 무작위 솔트(salt)를 생성하고, PBKDF2로 수십만 번 반복(stretching)해
 * 저장용 해시를 만든다.
 *   - 솔트가 달라 같은 비밀번호라도 해시가 매번 다르다(레인보우 테이블 무력화).
 *   - 반복 횟수를 높여 무차별 대입 비용을 크게 늘린다.
 * (bcrypt, scrypt, Argon2 같은 전용 알고리즘을 써도 좋다.)
 *
 * 안전 지점:
 *   - SecureRandom 으로 salt 생성
 *   - PBKDF2WithHmacSHA256 으로 반복 해싱
 */
public class Secure {

    private static final int ITERATIONS = 210_000;
    private static final int KEY_LEN = 256;

    /** 저장 형식: base64(salt):base64(hash) */
    public String hashPassword(String rawPassword) throws Exception {
        // ★ 안전: 사용자마다 다른 무작위 salt 를 만든다.
        byte[] salt = new byte[16];
        new SecureRandom().nextBytes(salt);

        byte[] hash = pbkdf2(rawPassword.toCharArray(), salt);
        return Base64.getEncoder().encodeToString(salt) + ":"
                + Base64.getEncoder().encodeToString(hash);
    }

    /** 저장된 salt 로 재계산해 상수시간 비교로 검증한다. */
    public boolean verifyPassword(String rawPassword, String stored) throws Exception {
        String[] parts = stored.split(":");
        byte[] salt = Base64.getDecoder().decode(parts[0]);
        byte[] expected = Base64.getDecoder().decode(parts[1]);
        byte[] actual = pbkdf2(rawPassword.toCharArray(), salt);
        return java.security.MessageDigest.isEqual(expected, actual);
    }

    private byte[] pbkdf2(char[] pw, byte[] salt) throws Exception {
        KeySpec spec = new PBEKeySpec(pw, salt, ITERATIONS, KEY_LEN);
        SecretKeyFactory f = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        return f.generateSecret(spec).getEncoded();
    }

    public static void main(String[] args) throws Exception {
        Secure s = new Secure();
        String h1 = s.hashPassword("hunter2");
        String h2 = s.hashPassword("hunter2");
        System.out.println("같은 비밀번호라도 해시가 다름: " + !h1.equals(h2));
        System.out.println("검증 성공? " + s.verifyPassword("hunter2", h1));
    }
}
