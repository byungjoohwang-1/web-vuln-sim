import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;

/**
 * [취약 예제] 경로 조작 및 자원 삽입 (CWE-22 / KISA 4.3)
 *
 * 외부 입력(파일명)을 기준 경로에 문자열로 이어 붙여 파일에 접근한다.
 * 공격자가 "../../../etc/passwd" 같은 상위 경로 이동 문자열을 넣으면
 * 의도한 디렉터리를 벗어나 시스템 파일을 읽을 수 있다.
 *
 * 위험 지점:
 *   new File(baseDir + name), new FileInputStream(baseDir + name)
 */
public class Vulnerable {

    static final String BASE_DIR = "/var/app/uploads/";

    /** HTTP 요청 파라미터 흉내 헬퍼. */
    static String req(String name) {
        // 예: name = "../../../../etc/passwd"
        return "report.pdf";
    }

    public InputStream openDownload() throws Exception {
        String name = req("name"); // 신뢰할 수 없는 외부 입력

        // ★ 취약: 기준 경로에 입력을 그대로 연결한다. 경로 이동 검증이 전혀 없다.
        File target = new File(BASE_DIR + name);
        InputStream in = new FileInputStream(BASE_DIR + name);
        System.out.println("여는 파일: " + target.getPath());
        return in;
    }

    public static void main(String[] args) throws Exception {
        new Vulnerable().openDownload().close();
    }
}
