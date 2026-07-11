import java.security.cert.X509Certificate;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

/**
 * [취약 예제] 부적절한 인증서 유효성 검증 (CWE-295 / KISA 2.11)
 *
 * 서버 인증서를 전혀 검증하지 않는 "모두 신뢰(Trust-All)" TrustManager를 설치한다.
 * checkServerTrusted() 본문이 비어 있어, 만료·자가서명·다른 도메인 인증서까지
 * 무조건 통과된다. 이는 중간자 공격(MITM)에 그대로 노출되는 대표적 실수다.
 *
 * 위험 지점:
 *   public void checkServerTrusted(X509Certificate[] c, String t) {}  // 검증 없음
 */
public class Vulnerable {

    /** ★ 취약: 아무것도 검증하지 않는 TrustManager. */
    static TrustManager trustAll() {
        return new X509TrustManager() {
            @Override
            public void checkClientTrusted(X509Certificate[] chain, String authType) {}

            @Override
            public void checkServerTrusted(X509Certificate[] chain, String authType) {}

            @Override
            public X509Certificate[] getAcceptedIssuers() {
                return new X509Certificate[0];
            }
        };
    }

    public SSLContext buildContext() throws Exception {
        SSLContext ctx = SSLContext.getInstance("TLS");
        // ★ 취약: 검증을 하지 않는 TrustManager를 설치한다 → 어떤 서버든 신뢰.
        ctx.init(null, new TrustManager[] { trustAll() }, null);
        return ctx;
    }

    public static void main(String[] args) throws Exception {
        System.out.println("취약 예제: Trust-All 은 위조 인증서까지 통과시킨다.");
    }
}
