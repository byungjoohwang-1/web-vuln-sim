import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

/**
 * [취약 예제] TOCTOU 경쟁조건 (CWE-367 / KISA 시간 및 상태)
 *
 * 파일이 존재하는지 "검사(Check)"하는 시점과, 그 결과를 믿고
 * 파일을 "사용(Use)"하는 시점 사이에 시간 간격이 생긴다.
 * 이 간격 동안 다른 프로세스/스레드가 파일을 만들거나 심볼릭 링크로
 * 바꿔치기하면, 검사 결과가 더 이상 참이 아니게 된다.
 *
 * 위험 지점:
 *   file.exists() 로 없음을 확인한 뒤 → 다시 열어서 쓰기 (검사와 사용 분리)
 */
public class Vulnerable {

    /**
     * 임시 잠금 파일을 만들어 "내가 처음 진입한 프로세스"임을 표시하려는 로직.
     * 하지만 검사(exists)와 생성(FileWriter) 사이가 원자적이지 않다.
     */
    public boolean acquireLock(String path) throws IOException {
        File lock = new File(path);

        // ★ 취약: 여기서 "없음"을 확인한다 (Time Of Check)
        if (lock.exists()) {
            // 이미 다른 프로세스가 잠금을 잡았다고 판단하고 포기
            return false;
        }

        // ... 이 사이(윈도우)에 다른 프로세스가 같은 파일을 만들 수 있다 ...
        // 그러면 아래에서 남의 잠금 파일을 덮어써 버린다 (Time Of Use)
        try (FileWriter w = new FileWriter(lock)) {
            w.write("locked-by-" + Thread.currentThread().getId());
        }
        return true;
    }

    public static void main(String[] args) throws IOException {
        Vulnerable v = new Vulnerable();
        System.out.println("lock acquired = " + v.acquireLock("app.lock"));
    }
}
