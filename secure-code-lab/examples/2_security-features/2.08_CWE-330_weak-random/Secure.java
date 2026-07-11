import java.security.SecureRandom;

/**
 * [안전 예제] 안전한 난수 값 사용 (CWE-330 / KISA 2.8)
 *
 * 보안에 사용되는 값은 암호학적으로 안전한 난수생성기(CSPRNG)인
 * java.security.SecureRandom 으로 생성한다.
 * 출력이 예측 불가능하므로 토큰/세션/OTP 등에 사용해도 안전하다.
 *
 * 완화 지표:
 *   SecureRandom 사용.
 */
public class Secure {

    // ★ 안전: 암호학적으로 안전한 난수생성기(CSPRNG)
    private final SecureRandom rnd = new SecureRandom();

    /** 예측 불가능한 비밀번호 재설정 토큰을 생성한다. */
    public String resetToken() {
        StringBuilder sb = new StringBuilder();
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        for (int i = 0; i < 16; i++) {
            int idx = rnd.nextInt(chars.length()); // SecureRandom.nextInt
            sb.append(chars.charAt(idx));
        }
        return sb.toString();
    }

    /** 6자리 OTP 생성(예측 불가능). */
    public String otp() {
        int code = rnd.nextInt(1_000_000);
        return String.format("%06d", code);
    }

    public static void main(String[] args) {
        Secure s = new Secure();
        // ★ 안전: 비밀값(예: HMAC 키)은 소스에 두지 않고 환경변수에서 읽는다.
        String hmacKey = System.getenv("RESET_TOKEN_KEY");
        System.out.println("resetToken=" + s.resetToken());
        System.out.println("otp=" + s.otp());
        System.out.println("keyLoaded=" + (hmacKey != null));
    }
}
