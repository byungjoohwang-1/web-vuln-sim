import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * [안전 예제] 부적절한 예외 처리 방지 (CWE-755 / KISA 에러처리)
 *
 * 발생 가능한 예외를 유형별로 구체적으로 잡아, 각 상황에 맞게
 * 대응한다. 광범위한 catch(Exception)/catch(Throwable)를 쓰지 않으므로
 * 프로그래밍 버그(RuntimeException)까지 함께 삼켜지는 일이 없다.
 *
 *   - IOException          → 파일 접근 실패(로그 후 기본값 사용)
 *   - NumberFormatException → 형식 오류(로그 후 기본값 사용)
 *
 * 위 두 가지에 해당하지 않는 예상치 못한 예외는 잡지 않고
 * 그대로 전파시켜, 진짜 버그가 드러나도록 한다.
 *
 * 안전 지표:
 *   구체적 예외(IOException, NumberFormatException)만 개별 처리
 */
public class Secure {

    private static final Logger logger = Logger.getLogger(Secure.class.getName());

    /**
     * 파일에서 첫 줄을 읽어 정수로 파싱한다.
     *
     * @param defaultValue 읽기/파싱 실패 시 사용할 안전한 기본값
     */
    public int readNumber(String path, int defaultValue) {
        List<String> lines;
        try {
            lines = Files.readAllLines(Paths.get(path));
        } catch (IOException io) {
            // ★ 안전: 파일 접근 실패만 구체적으로 처리
            logger.log(Level.WARNING, "파일을 읽을 수 없습니다: " + path, io);
            return defaultValue;
        }

        if (lines.isEmpty()) {
            logger.warning("파일이 비어 있습니다: " + path);
            return defaultValue;
        }

        try {
            return Integer.parseInt(lines.get(0).trim());
        } catch (NumberFormatException nfe) {
            // ★ 안전: 숫자 형식 오류만 구체적으로 처리
            logger.log(Level.WARNING, "숫자 형식이 아닙니다: " + lines.get(0), nfe);
            return defaultValue;
        }
        // 그 밖의 예상치 못한 예외는 잡지 않고 그대로 전파된다.
    }

    public static void main(String[] args) {
        Secure s = new Secure();
        System.out.println("value = " + s.readNumber("number.txt", 0));
    }
}
