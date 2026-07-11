import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

/**
 * [안전 예제] TOCTOU 방지 (CWE-367 / KISA 시간 및 상태)
 *
 * 핵심: "검사"와 "사용"을 하나의 원자적(atomic) 연산으로 합친다.
 * 존재 여부를 미리 exists()로 물어보지 않고, 운영체제가 보장하는
 * "없을 때만 생성" 연산 하나로 시도한다. 이미 있으면 예외로 실패한다.
 *
 * 사용 API:
 *   StandardOpenOption.CREATE_NEW  → 파일이 없을 때만 새로 생성(원자적)
 *   Files.createFile               → 존재 시 FileAlreadyExistsException 발생
 *
 * 이렇게 하면 검사~사용 사이의 경쟁조건 윈도우 자체가 사라진다.
 */
public class Secure {

    /**
     * 원자적 "없을 때만 생성"으로 잠금을 획득한다.
     * 이미 파일이 있으면 생성 자체가 실패하므로 검사할 필요가 없다.
     */
    public boolean acquireLock(String path) {
        Path lock = Paths.get(path);
        // ★ 안전: CREATE_NEW 는 파일이 이미 존재하면 원자적으로 실패한다.
        //   exists() 로 미리 확인하지 않으므로 TOCTOU 윈도우가 없다.
        try (OutputStream out = Files.newOutputStream(
                lock,
                StandardOpenOption.CREATE_NEW,
                StandardOpenOption.WRITE)) {
            out.write(("locked-by-" + Thread.currentThread().getId())
                    .getBytes(StandardCharsets.UTF_8));
            return true;
        } catch (FileAlreadyExistsException already) {
            // 다른 프로세스가 이미 잠금을 잡았음 — 정상적인 경쟁 결과
            return false;
        } catch (IOException io) {
            // 그 외 입출력 오류는 획득 실패로 처리
            return false;
        }
    }

    /**
     * 참고: createFile 도 동일하게 원자적으로 동작한다.
     */
    public boolean acquireLockAlt(String path) {
        try {
            Files.createFile(Paths.get(path));
            return true;
        } catch (FileAlreadyExistsException already) {
            return false;
        } catch (IOException io) {
            return false;
        }
    }

    public static void main(String[] args) {
        Secure s = new Secure();
        System.out.println("lock acquired = " + s.acquireLock("app.lock"));
    }
}
