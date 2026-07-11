import java.net.InetAddress;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.logging.Logger;

/**
 * [안전 예제] DNS 이름에 의존하지 않는 보안결정 (CWE-350 / KISA 7.01 API 오용)
 *
 * 안전한 코딩:
 *   보안 결정은 위조 가능한 역방향 DNS 이름이 아니라, 실제 접속 IP 주소로 한다.
 *   - addr.getHostAddress() 로 원시 IP 문자열을 얻는다(DNS 조회 없음).
 *   - 사전에 정의한 IP 허용목록(ALLOWLIST)과 정확히 비교한다.
 *   이름 기반 신뢰가 꼭 필요하면 상호 TLS 인증서 등 위조 불가한 수단을 쓴다.
 */
public class Secure {

    private static final Logger LOG = Logger.getLogger(Secure.class.getName());

    // ★ 안전: 신뢰 IP 허용목록(정적으로 관리)
    private static final Set<String> ALLOWLIST = new HashSet<>(Arrays.asList(
            "10.0.0.5",
            "10.0.0.6",
            "127.0.0.1"
    ));

    /**
     * ★ 안전: 역방향 DNS 이름이 아니라 원시 IP 주소로 판정한다.
     *   getHostAddress() 결과는 DNS 위조의 영향을 받지 않는다.
     */
    public boolean isTrusted(InetAddress addr) {
        String ip = addr.getHostAddress(); // 이름 조회 없이 실제 IP 문자열
        return ALLOWLIST.contains(ip);
    }

    public static void main(String[] args) throws Exception {
        Secure s = new Secure();
        InetAddress client = InetAddress.getByName("127.0.0.1");
        LOG.info("trusted = " + s.isTrusted(client));
    }
}
