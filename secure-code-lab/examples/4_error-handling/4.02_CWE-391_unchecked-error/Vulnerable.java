import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * [취약 예제] 오류상황 대응 부재 / 빈 catch (CWE-391 / KISA 에러처리)
 *
 * 예외를 잡기만 하고 아무 처리도 하지 않는 "빈 catch"이다.
 * 오류가 나도 조용히 삼켜지므로, 설정 로딩이 실패했는데도
 * 프로그램은 아무 일 없었던 것처럼 진행한다. 그 결과 이후 로직이
 * 빈 설정으로 오작동하고, 원인 추적도 불가능해진다.
 *
 * 위험 지점:
 *   catch (IOException e) { }  ← 아무 대응 없이 예외를 삼킴
 */
public class Vulnerable {

    private final Properties config = new Properties();

    /**
     * 설정 파일을 읽는다. 실패해도 아무 대응이 없다.
     */
    public void loadConfig(String path) {
        InputStream in = null;
        try {
            in = new FileInputStream(path);
            config.load(in);
            System.out.println("설정 로딩 성공");
        } catch (IOException e) {
            // ★ 취약: 예외를 잡고 그냥 무시한다(빈 블록).
            //   오류가 발생했다는 사실조차 어디에도 남지 않는다.
        }
        // in 을 닫지 않아 자원 누수까지 겹칠 수 있다.
    }

    public static void main(String[] args) {
        Vulnerable v = new Vulnerable();
        // 존재하지 않는 파일이어도 오류가 조용히 사라진다.
        v.loadConfig("app.properties");
        System.out.println("mode = " + v.config.getProperty("mode", "(기본값)"));
    }
}
