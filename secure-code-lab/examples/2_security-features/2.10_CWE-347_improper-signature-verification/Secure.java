import java.security.PublicKey;
import java.security.Signature;

/**
 * [안전 예제] 전자서명 결과를 반드시 확인 (CWE-347 / KISA 2.10)
 *
 * verify()가 돌려주는 boolean 결과를 조건문으로 반드시 확인하고,
 * 검증에 실패하면 처리 자체를 중단(예외/거부)한다.
 *
 * 안전 지점:
 *   boolean verified = sig.verify(sigBytes);
 *   if (verified) { ... } else { 거부 }
 */
public class Secure {

    /**
     * 메시지와 서명을 받아 검증 결과에 따라 분기한다.
     * ★ 안전: verify() 결과를 변수/조건문으로 확인하고, 실패 시 예외를 던진다.
     */
    public String process(byte[] message, byte[] sigBytes, PublicKey pubKey)
            throws Exception {
        Signature sig = Signature.getInstance("SHA256withRSA");
        sig.initVerify(pubKey);
        sig.update(message);

        // ★ 안전: 반환값을 반드시 확인한다.
        boolean verified = sig.verify(sigBytes);
        if (verified) {
            return "서명 검증 성공, 신뢰하고 처리함: " + new String(message);
        }
        // 검증 실패는 조용히 넘기지 않고 명확히 거부한다.
        throw new SecurityException("전자서명 검증 실패: 위조되었거나 손상된 메시지");
    }

    public static void main(String[] args) throws Exception {
        System.out.println("안전 예제: verify() 결과를 조건문으로 확인하고 실패 시 거부한다.");
    }
}
