/**
 * [안전 예제] 주석에 민감정보를 남기지 않음 (CWE-615 / KISA 2.13)
 *
 * 접속 정보와 자격증명은 소스나 주석에 두지 않고, 외부 설정/환경변수에서 읽는다.
 * 아래 주석 어디에도 실제 호스트, 비밀번호, API 키가 등장하지 않는다.
 * (설명은 "무엇을 하는지"만 말하고, "비밀값이 무엇인지"는 말하지 않는다.)
 *
 * 안전 지점:
 *   - 연결 정보는 환경변수/설정에서 로드
 *   - 주석에는 값이 아니라 의도만 기록
 */
public class Secure {

    /** DB 연결 문자열을 외부 설정 기반으로 만든다. */
    public String buildConnectionString() {
        // 연결 정보는 배포 환경의 설정에서 주입받는다. 값은 코드/주석에 두지 않는다.
        String host = readConfig("db.host");
        String db = readConfig("db.name");
        String port = readConfig("db.port");
        return "jdbc:mysql://" + host + ":" + port + "/" + db;
    }

    /** 환경변수 또는 보안 저장소에서 설정을 읽는다(값은 노출하지 않음). */
    private String readConfig(String key) {
        String fromEnv = System.getenv(key);
        return fromEnv != null ? fromEnv : "(주입된 설정값)";
    }

    public static void main(String[] args) {
        System.out.println("안전 예제: 주석과 코드 어디에도 실제 자격증명이 없다.");
    }
}
