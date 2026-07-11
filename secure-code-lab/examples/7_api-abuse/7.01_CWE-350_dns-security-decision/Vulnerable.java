import java.net.InetAddress;

/**
 * [취약 예제] DNS lookup에 의존한 보안결정 (CWE-350 / KISA 7.01 API 오용)
 *
 * 개념:
 *   접속 클라이언트의 "호스트 이름"으로 접근 허용 여부를 결정하는 방식은 위험하다.
 *   호스트 이름은 역방향 DNS(reverse DNS)로 얻는데, 이 조회는
 *   공격자가 통제하는 DNS 서버/레코드에 의해 위조될 수 있다.
 *   즉 IP 는 통제 밖의 값이지만, 그 IP 에 대응되는 이름은 공격자가 꾸밀 수 있다.
 *
 * 위험 지점:
 *   addr.getHostName() 으로 얻은 이름이 사내 도메인으로 끝나면 신뢰한다.
 */
public class Vulnerable {

    /**
     * ★ 취약: 역방향 DNS 이름으로 접근을 허용한다.
     *   공격자가 자신의 IP 의 PTR 레코드를 "*.internal.example.com" 으로 위조하면
     *   내부 사용자로 오인되어 통과한다.
     */
    public boolean isTrusted(InetAddress addr) {
        String hostName = addr.getHostName(); // 역방향 DNS 조회 (신뢰 불가)
        return hostName.endsWith(".internal.example.com");
    }

    public static void main(String[] args) throws Exception {
        Vulnerable v = new Vulnerable();
        InetAddress client = InetAddress.getByName("127.0.0.1");
        System.out.println("trusted = " + v.isTrusted(client));
    }
}
