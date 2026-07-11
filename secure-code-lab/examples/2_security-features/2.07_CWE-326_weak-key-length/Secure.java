import java.security.KeyPair;
import java.security.KeyPairGenerator;

/**
 * [안전 예제] 충분한 키 길이 사용 (CWE-326 / KISA 2.7)
 *
 * RSA 키를 2048비트 이상으로 생성한다. 현재 권고 최소치는 2048비트이며,
 * 장기 보관용이라면 3072/4096비트를 고려한다.
 *
 * 완화 지표:
 *   keyGen.initialize(2048)  ← 권고 이상의 키 길이
 */
public class Secure {

    public KeyPair generateRsa() throws Exception {
        KeyPairGenerator keyGen = KeyPairGenerator.getInstance("RSA");

        // ★ 안전: 2048비트 RSA 키 (권고 충족). 장기용은 3072/4096 고려.
        keyGen.initialize(2048);

        return keyGen.generateKeyPair();
    }

    public static void main(String[] args) throws Exception {
        KeyPair kp = new Secure().generateRsa();
        System.out.println("public key algo=" + kp.getPublic().getAlgorithm());
    }
}
