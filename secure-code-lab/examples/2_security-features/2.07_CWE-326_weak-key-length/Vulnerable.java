import java.security.KeyPair;
import java.security.KeyPairGenerator;

/**
 * [취약 예제] 충분하지 않은 키 길이 사용 (CWE-326 / KISA 2.7)
 *
 * RSA 키를 1024비트로 생성한다. 1024비트 RSA는 계산 능력 향상으로
 * 더 이상 안전하다고 보지 않으며(현대 권고는 2048비트 이상),
 * 충분한 자원을 가진 공격자가 인수분해로 개인키를 복원할 수 있다.
 *
 * 위험 지점:
 *   keyGen.initialize(1024)  ← 너무 짧은 키 길이
 */
public class Vulnerable {

    public KeyPair generateRsa() throws Exception {
        KeyPairGenerator keyGen = KeyPairGenerator.getInstance("RSA");

        // ★ 취약: 1024비트 RSA 키 (권고 미달)
        keyGen.initialize(1024);

        return keyGen.generateKeyPair();
    }

    public static void main(String[] args) throws Exception {
        KeyPair kp = new Vulnerable().generateRsa();
        System.out.println("public key algo=" + kp.getPublic().getAlgorithm());
    }
}
