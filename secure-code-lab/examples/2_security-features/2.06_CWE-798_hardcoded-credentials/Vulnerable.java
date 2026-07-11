import java.sql.Connection;
import java.sql.DriverManager;

/**
 * [취약 예제] 하드코드된 중요정보 (CWE-798 / KISA 2.6)
 *
 * DB 비밀번호, API 키 같은 인증정보를 소스코드에 문자열 상수로 박아 넣었다.
 * 소스가 유출되거나(사내 저장소, 디컴파일, 실수 커밋) 배포 산출물을 분석당하면
 * 인증정보가 그대로 노출되며, 값 변경 시 재빌드/재배포가 필요해 대응도 늦다.
 *
 * 위험 지점:
 *   String password = "..." / String apiKey = "..." 처럼 비밀정보 하드코딩.
 */
public class Vulnerable {

    // ★ 취약: 비밀번호를 소스에 하드코딩
    private static final String password = "P@ss1234!";
    // ★ 취약: API 키를 소스에 하드코딩
    private static final String apiKey = "sk_live_ABCD1234EFGH5678";

    public Connection connect() throws Exception {
        // 하드코딩된 비밀번호로 DB에 접속
        return DriverManager.getConnection(
                "jdbc:mysql://localhost:3306/app", "app_user", password);
    }

    public String callPaymentApi() {
        // 하드코딩된 키로 외부 API 호출 (개념 시연)
        return "Authorization: Bearer " + apiKey;
    }

    public static void main(String[] args) {
        System.out.println(new Vulnerable().callPaymentApi());
    }
}
