import java.security.PublicKey;
import java.security.Signature;

/**
 * [취약 예제] 부적절한 전자서명 확인 (CWE-347 / KISA 2.10)
 *
 * 전자서명을 검증하긴 하지만, verify()가 돌려주는 boolean 결과를 무시한다.
 * 즉 서명이 유효하든 위조되었든 상관없이 이후 로직이 그대로 진행된다.
 * 공격자는 아무 서명이나 붙여 위조 메시지를 정상 메시지처럼 처리하게 만들 수 있다.
 *
 * 위험 지점:
 *   sig.verify(sigBytes);   // 반환값을 버린다 → 검증이 사실상 무의미
 */
public class Vulnerable {

    /**
     * 메시지와 서명을 받아 "검증했다고 착각"하고 처리한다.
     * ★ 취약: verify()의 결과를 조건문/변수에 담지 않고 버린다.
     */
    public String process(byte[] message, byte[] sigBytes, PublicKey pubKey)
            throws Exception {
        Signature sig = Signature.getInstance("SHA256withRSA");
        sig.initVerify(pubKey);
        sig.update(message);

        // ★ 취약: 반환값을 무시한다. 서명이 틀려도 예외가 아니라 그냥 false일 뿐이다.
        sig.verify(sigBytes);

        // 검증에 실패했더라도 여기까지 그대로 도달한다.
        return "메시지를 신뢰하고 처리함: " + new String(message);
    }

    public static void main(String[] args) throws Exception {
        System.out.println("취약 예제: verify() 결과를 무시하면 위조 서명도 통과한다.");
    }
}
