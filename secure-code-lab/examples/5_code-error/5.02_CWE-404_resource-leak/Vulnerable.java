import java.io.FileInputStream;
import java.io.IOException;

/**
 * [취약 예제] 부적절한 자원 해제 (CWE-404 / KISA 5.02)
 *
 * FileInputStream 을 열고 사용한 뒤 close() 하지 않는다.
 * 예외가 나든 정상 종료든 스트림이 닫히지 않아 파일 핸들이 누수된다.
 * 이런 코드가 반복 호출되면 OS 파일 디스크립터가 고갈되어
 * "Too many open files" 오류로 서비스가 마비될 수 있다.
 *
 * 위험 지점:
 *   new FileInputStream(path) 를 열고 스트림을 닫는 처리가 전혀 없음
 */
public class Vulnerable {

    public int countBytes(String path) throws IOException {
        // ★ 취약: 스트림을 열지만 어디서도 닫지 않는다.
        //   중간에 IOException 이 나면 핸들은 그대로 새어나간다.
        FileInputStream fis = new FileInputStream(path);
        int total = 0;
        while (fis.read() != -1) {
            total = total + 1;
        }
        // close() 호출 없음 → 자원 누수
        return total;
    }

    public static void main(String[] args) throws IOException {
        String path = args.length > 0 ? args[0] : "Vulnerable.java";
        System.out.println("bytes=" + new Vulnerable().countBytes(path));
    }
}
