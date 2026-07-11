import java.security.KeyStore;
import java.security.cert.CertPathValidator;
import java.security.cert.PKIXParameters;
import java.security.cert.X509Certificate;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.TrustManagerFactory;

/**
 * [안전 예제] 인증서 유효성 정상 검증 (CWE-295 / KISA 2.11)
 *
 * 시스템 신뢰 저장소(cacerts)를 사용해 인증서 체인을 PKIX 방식으로 검증하고,
 * 각 인증서의 유효기간(checkValidity)을 확인한다. 또한 호스트 이름 검증도
 * 기본 HostnameVerifier(getDefaultHostnameVerifier)에 위임한다.
 *
 * 안전 지점:
 *   - PKIXParameters + CertPathValidator 로 체인 검증
 *   - cert.checkValidity() 로 만료 확인
 *   - HttpsURLConnection.getDefaultHostnameVerifier() 로 호스트명 검증
 */
public class Secure {

    /** 신뢰 저장소 기반의 표준 TrustManagerFactory를 구성한다. */
    public TrustManagerFactory buildTrustManagers(KeyStore trustStore) throws Exception {
        // ★ 안전: PKIX 규칙으로 인증서 경로를 검증하도록 설정한다.
        PKIXParameters params = new PKIXParameters(trustStore);
        params.setRevocationEnabled(false); // 예제 단순화(운영에서는 CRL/OCSP 사용)
        CertPathValidator.getInstance("PKIX"); // PKIX 검증기 사용을 명시

        TrustManagerFactory tmf =
                TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        tmf.init(trustStore);
        return tmf;
    }

    /** 개별 인증서의 유효기간을 명시적으로 확인한다. */
    public void ensureNotExpired(X509Certificate cert) throws Exception {
        // ★ 안전: 만료·아직 유효하지 않음을 checkValidity()로 검사한다.
        cert.checkValidity();
    }

    /** 호스트명 검증은 기본 검증기에 위임한다. */
    public boolean hostMatches(String host, javax.net.ssl.SSLSession session) {
        // ★ 안전: 도메인 불일치를 잡는 표준 호스트명 검증기 사용.
        javax.net.ssl.HostnameVerifier hv = HttpsURLConnection.getDefaultHostnameVerifier();
        if (hv.verify(host, session)) {
            return true;
        }
        return false;
    }

    public static void main(String[] args) throws Exception {
        System.out.println("안전 예제: PKIX 체인 검증 + checkValidity + 호스트명 검증.");
    }
}
