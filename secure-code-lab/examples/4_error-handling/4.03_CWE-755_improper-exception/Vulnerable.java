import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * [취약 예제] 부적절한 예외 처리 (CWE-755 / KISA 에러처리)
 *
 * 서로 성격이 다른 여러 예외를 하나의 광범위한 catch(Exception)로
 * 뭉뚱그려 처리한다. 그 결과:
 *   - 숫자 변환 오류인지, 파일 입출력 오류인지 구분하지 못한다.
 *   - RuntimeException(널 참조 등 프로그래밍 버그)까지 함께 삼켜져
 *     진짜 버그가 정상 흐름처럼 감춰진다.
 *   - 각 오류에 맞는 복구 로직을 적용할 수 없다.
 *
 * 위험 지점:
 *   catch (Exception e) 로 모든 예외를 한꺼번에 처리
 */
public class Vulnerable {

    /**
     * 파일에서 첫 줄을 읽어 정수로 파싱한다.
     */
    public int readNumber(String path) {
        try {
            String first = Files.readAllLines(Paths.get(path)).get(0);
            return Integer.parseInt(first.trim());
        } catch (Exception e) {
            // ★ 취약: IOException, NumberFormatException, IndexOutOfBounds,
            //   NullPointerException 등 전혀 다른 오류를 하나로 처리한다.
            //   원인 구분도, 적절한 복구도 불가능하다.
            System.out.println("문제가 생겨 0을 사용합니다.");
            return 0;
        }
    }

    public static void main(String[] args) throws IOException {
        Vulnerable v = new Vulnerable();
        System.out.println("value = " + v.readNumber("number.txt"));
    }
}
