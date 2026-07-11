import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;

/**
 * [안전 예제] 경로 조작 방어 (CWE-22 / KISA 4.3)
 *
 * 입력을 붙인 뒤 정규화(canonical path)로 실제 경로를 확정하고,
 * 그 경로가 허용된 기준 디렉터리 안(startsWith)에 있는지 검사한다.
 * "../" 로 상위 디렉터리를 벗어나려는 시도를 정규화 후 차단한다.
 */
public class Secure {

    static final String BASE_DIR = "/var/app/uploads/";

    static String req(String name) {
        return "report.pdf";
    }

    public InputStream openDownload() throws Exception {
        String name = req("name");

        File baseCanonical = new File(BASE_DIR).getCanonicalFile();
        // 입력을 붙인 뒤 정규화하여 ../ 를 실제 경로로 해소한다.
        File target = new File(baseCanonical, name).getCanonicalFile();
        String canonicalPath = target.getCanonicalPath();

        // ★ 안전: 정규화된 경로가 반드시 기준 디렉터리 하위여야 한다.
        if (!canonicalPath.startsWith(baseCanonical.getCanonicalPath() + File.separator)) {
            throw new SecurityException("허용된 디렉터리를 벗어난 접근: " + canonicalPath);
        }

        return new FileInputStream(target);
    }

    public static void main(String[] args) throws Exception {
        new Secure().openDownload().close();
    }
}
