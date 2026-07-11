import java.io.FileInputStream;
import java.io.IOException;

/**
 * [안전 예제] 자원의 확실한 해제 (CWE-404 / KISA 5.02)
 *
 * try-with-resources 구문으로 FileInputStream 을 연다.
 * 블록을 벗어나는 순간(정상 종료든 예외든) JVM 이 close() 를 자동 호출하므로
 * 파일 핸들이 절대 새어나가지 않는다.
 *
 * 안전 지점:
 *   try (FileInputStream fis = new FileInputStream(path)) { ... }
 */
public class Secure {

    public int countBytes(String path) throws IOException {
        // ★ 안전: try-with-resources 가 블록 종료 시 fis.close() 를 보장한다.
        try (FileInputStream fis = new FileInputStream(path)) {
            int total = 0;
            while (fis.read() != -1) {
                total = total + 1;
            }
            return total;
        }
    }

    public static void main(String[] args) throws IOException {
        String path = args.length > 0 ? args[0] : "Secure.java";
        System.out.println("bytes=" + new Secure().countBytes(path));
    }
}
