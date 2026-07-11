/**
 * [취약 예제] 주석문 안에 포함된 시스템 주요정보 (CWE-615 / KISA 2.13)
 *
 * 개발자가 편의를 위해 접속 정보와 비밀번호를 소스 주석에 남겨두었다.
 * 소스가 유출되거나, 배포 산출물에 주석이 그대로 남으면(맵 파일·난독화 누락 등)
 * 공격자가 DB 접속 정보를 그대로 획득한다. 주석은 실행에 영향은 없지만
 * "정보"로서 매우 위험하다.
 *
 * 위험 지점(주석 자체가 취약점):
 *   // db password: ...
 *   // jdbc:mysql://...
 */
public class Vulnerable {

    /** DB 연결 문자열을 만든다. */
    public String buildConnectionString() {
        // 운영 DB 접속용 메모 — 절대 지우지 말 것(이라 적어두면 더 위험하다)
        // jdbc:mysql://prod-db.internal:3306/orders
        // db password: P@ssw0rd_prod_2021   // 실제 운영 비밀번호를 주석에 남김
        // apikey: sk_live_51H8kQ2eZvKf   // 결제 연동 키까지 노출
        String host = readConfig("db.host");
        String db = readConfig("db.name");
        return "jdbc:mysql://" + host + ":3306/" + db;
    }

    /** 실제로는 외부 설정에서 읽는다고 가정한다. */
    private String readConfig(String key) {
        return "(설정값)";
    }

    public static void main(String[] args) {
        System.out.println("취약 예제: 주석에 접속정보/비밀번호/키가 남아 있다.");
    }
}
