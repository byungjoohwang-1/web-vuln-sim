import java.io.InputStream;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * [취약 예제] 무결성 검사 없는 코드 다운로드 (CWE-494 / KISA 2.15)
 *
 * 원격 URL에서 실행 파일/플러그인을 내려받아 무결성(서명·체크섬) 확인 없이
 * 그대로 저장하고 실행한다. 네트워크가 변조되거나(중간자) 배포 서버가 침해되면
 * 공격자가 임의 코드를 삽입해 실행시킬 수 있다.
 *
 * 위험 지점:
 *   new URL(url).openStream()  // 받은 바이트를 검증 없이 그대로 저장/실행
 */
public class Vulnerable {

    /**
     * 원격에서 플러그인을 내려받아 저장하고 곧바로 실행한다.
     * ★ 취약: 다운로드한 바이트의 해시/서명을 전혀 확인하지 않는다.
     */
    public void downloadAndRun(String url) throws Exception {
        Path target = Paths.get(System.getProperty("java.io.tmpdir"), "plugin.jar");

        // ★ 취약: 스트림을 열어 받은 그대로 저장한다(검증 없음).
        try (InputStream in = new URL(url).openStream()) {
            Files.copy(in, target, java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        }

        // 검증 없이 방금 받은 코드를 실행한다.
        Runtime.getRuntime().exec(new String[] { "java", "-jar", target.toString() });
    }

    public static void main(String[] args) throws Exception {
        System.out.println("취약 예제: 검증 없이 내려받은 코드를 실행한다.");
    }
}
