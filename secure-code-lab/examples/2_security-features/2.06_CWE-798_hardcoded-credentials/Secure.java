import java.sql.Connection;
import java.sql.DriverManager;

/**
 * [안전 예제] 하드코드된 중요정보 제거 (CWE-798 / KISA 2.6)
 *
 * 인증정보를 소스코드에서 분리해 환경변수/시스템 속성/시크릿 저장소에서 읽는다.
 * 소스가 유출돼도 비밀정보는 노출되지 않고, 값 변경 시 재배포 없이 교체 가능하다.
 *
 * 완화 지표:
 *   System.getenv(...) / System.getProperty(...) 로 비밀정보를 외부에서 주입.
 */
public class Secure {

    /** 환경변수 우선, 없으면 시스템 속성에서 읽는다. 둘 다 없으면 실패 처리. */
    private static String requireSecret(String envKey, String propKey) {
        String v = System.getenv(envKey);
        if (v == null || v.isBlank()) {
            v = System.getProperty(propKey);
        }
        if (v == null || v.isBlank()) {
            throw new IllegalStateException("필수 비밀정보 미설정: " + envKey);
        }
        return v;
    }

    public java.util.List<String> connectAndListTables() throws Exception {
        // ★ 안전: 인증정보를 환경변수/시스템 속성에서 주입받는다(소스에 값이 없음).
        String secret = requireSecret("DB_PASSWORD", "db.password");
        java.util.List<String> tables = new java.util.ArrayList<>();
        // ★ 안전: try-with-resources 로 Connection 을 자동 해제한다(자원 누수 방지).
        try (Connection conn = DriverManager.getConnection(
                "jdbc:mysql://localhost:3306/app", "app_user", secret)) {
            tables.add(conn.getCatalog());
        }
        return tables;
    }

    public String callPaymentApi() {
        // ★ 안전: API 키도 환경변수/시크릿에서 주입받는다.
        String apiKey = requireSecret("PAYMENT_API_KEY", "payment.api.key");
        return "Authorization: Bearer " + apiKey;
    }

    private static final java.util.logging.Logger logger =
            java.util.logging.Logger.getLogger(Secure.class.getName());

    public static void main(String[] args) {
        // 실행 전 환경변수 설정 필요:  export PAYMENT_API_KEY=...
        try {
            System.out.println(new Secure().callPaymentApi());
        } catch (IllegalStateException e) {
            // ★ 안전: 상세 원인은 로거로만 기록하고, 사용자에게는 일반 안내만.
            logger.log(java.util.logging.Level.WARNING, "필수 환경변수 미설정", e);
            System.out.println("환경변수를 설정하세요.");
        }
    }
}
