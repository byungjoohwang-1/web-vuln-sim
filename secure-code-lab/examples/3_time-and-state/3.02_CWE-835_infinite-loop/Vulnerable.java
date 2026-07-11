import java.util.ArrayDeque;
import java.util.Queue;

/**
 * [취약 예제] 종료되지 않는 반복문 (CWE-835 / KISA 시간 및 상태)
 *
 * while(true) 루프가 종료 조건 없이 돈다. 큐가 비어도 빠져나갈
 * 경로가 없어 CPU 를 100% 점유하며 무한히 회전한다(라이브락/행).
 * 소비자 스레드가 이런 구조면 서비스 전체가 멈춘 것처럼 보인다.
 *
 * 위험 지점:
 *   while (true) { ... } 안에 탈출 경로가 존재하지 않음
 */
public class Vulnerable {

    private final Queue<String> jobs = new ArrayDeque<>();

    public void enqueue(String job) {
        jobs.add(job);
    }

    /**
     * 작업 큐를 소비하는 워커.
     * ★ 취약: 조건 없는 무한 루프. 큐가 비면 처리할 것이 없는데도
     *   루프를 빠져나가는 경로가 없어 바쁜 대기(busy-wait)로 돈다.
     */
    public void runWorker() {
        while (true) {
            String job = jobs.poll();
            if (job != null) {
                // 실제로는 작업을 처리하는 부분
                System.out.println("처리: " + job);
            }
            // 큐가 비어도 계속 while(true) 로 되돌아온다 → 영원히 회전
        }
    }

    public static void main(String[] args) {
        Vulnerable v = new Vulnerable();
        v.enqueue("A");
        v.enqueue("B");
        // 주의: 아래 호출은 영원히 끝나지 않는다 (데모용으로만 존재)
        v.runWorker();
    }
}
