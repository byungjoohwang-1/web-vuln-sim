import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * [안전 예제] 오류상황 대응 (CWE-391 / KISA 에러처리)
 *
 * 예외를 삼키지 않는다. 잡은 예외는 반드시 다음 중 하나로 처리한다.
 *   1) 로깅하여 원인을 남기고,
 *   2) 호출자가 알 수 있도록 의미 있는 예외로 다시 던지거나 복구한다.
 *
 * 여기서는 상세 원인을 logger 로 기록한 뒤, 설정 로딩 실패를
 * 명확한 예외로 다시 던져 호출자가 대응하도록 한다.
 *
 * 안전 지표:
 *   catch 블록에서 logger 기록 + 의미 있는 예외 재던지기(throw)
 */
public class Secure {

    private static final Logger logger = Logger.getLogger(Secure.class.getName());
    private final Properties config = new Properties();

    /**
     * 설정 파일을 읽는다. 실패 시 로깅 후 예외를 다시 던진다.
     */
    public void loadConfig(String path) {
        Path p = Paths.get(path);
        try (InputStream in = Files.newInputStream(p)) {   // 자원 자동 해제
            config.load(in);
            logger.info("설정 로딩 성공: " + path);
        } catch (IOException e) {
            // ★ 안전: 원인을 로그로 남기고, 무시하지 않고 다시 던진다.
            logger.log(Level.SEVERE, "설정 로딩 실패: " + path, e);
            throw new IllegalStateException("설정을 불러올 수 없습니다: " + path, e);
        }
    }

    public String get(String key) {
        return config.getProperty(key, "(기본값)");
    }

    public static void main(String[] args) {
        Secure s = new Secure();
        try {
            s.loadConfig("app.properties");
        } catch (IllegalStateException e) {
            // 호출자가 실패를 인지하고 대체 경로로 대응할 수 있다.
            logger.warning("기본 설정으로 계속 진행합니다.");
        }
        System.out.println("mode = " + s.get("mode"));
    }
}
