import java.util.Random;

/**
 * [취약 예제] 적절하지 않은 난수 값 사용 (CWE-330 / KISA 2.8)
 *
 * 보안에 사용되는 값(비밀번호 재설정 토큰, 세션 식별자, OTP 등)을
 * java.util.Random / Math.random() 으로 생성한다.
 * 이들은 선형 합동 방식의 의사난수로, 시드가 예측되거나 출력 몇 개만 관찰하면
 * 이후 값을 계산해낼 수 있어 보안 용도로 부적합하다.
 *
 * 위험 지점:
 *   new Random() / Math.random() 으로 보안 토큰 생성.
 */
public class Vulnerable {

    // ★ 취약: 예측 가능한 의사난수 생성기 (시드 기반, 보안용 아님)
    private final Random rnd = new Random();

    /** 비밀번호 재설정 토큰을 생성한다(예측 가능). */
    public String resetToken() {
        StringBuilder sb = new StringBuilder();
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        for (int i = 0; i < 16; i++) {
            // ★ 취약: Random.nextInt / Math.random 은 예측 가능
            int idx = rnd.nextInt(chars.length());
            sb.append(chars.charAt(idx));
        }
        return sb.toString();
    }

    /** 6자리 OTP 생성(예측 가능). */
    public String otp() {
        int code = (int) (Math.random() * 1_000_000); // ★ 취약
        return String.format("%06d", code);
    }

    public static void main(String[] args) {
        Vulnerable v = new Vulnerable();
        System.out.println("token=" + v.resetToken());
        System.out.println("otp=" + v.otp());
    }
}
