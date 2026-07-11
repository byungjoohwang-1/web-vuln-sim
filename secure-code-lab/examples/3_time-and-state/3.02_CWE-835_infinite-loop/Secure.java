import java.util.ArrayDeque;
import java.util.Queue;

/**
 * [안전 예제] 경계 있는 반복문 (CWE-835 / KISA 시간 및 상태)
 *
 * 반복문은 반드시 종료 조건을 가져야 한다. 여기서는 두 가지 안전장치를
 * 둔다.
 *   1) 큐가 비면 처리할 작업이 없으므로 루프를 벗어난다.
 *   2) 최대 반복 횟수(maxIter)를 두어, 예기치 못한 상황에서도
 *      무한 회전하지 않도록 상한을 강제한다.
 *
 * 안전 지표:
 *   counter < maxIter 상한, 큐 소진 시 break 로 정상 종료
 */
public class Secure {

    private final Queue<String> jobs = new ArrayDeque<>();

    public void enqueue(String job) {
        jobs.add(job);
    }

    /**
     * 작업 큐를 소비하는 워커. 종료 조건이 명확하다.
     *
     * @param maxIter 안전을 위한 최대 반복 횟수 상한
     */
    public void runWorker(int maxIter) {
        int counter = 0;
        while (counter < maxIter) {          // ★ 안전: 반복 횟수 상한
            String job = jobs.poll();
            if (job == null) {
                break;                       // ★ 안전: 큐 소진 시 정상 종료
            }
            System.out.println("처리: " + job);
            counter++;
        }
    }

    public static void main(String[] args) {
        Secure s = new Secure();
        s.enqueue("A");
        s.enqueue("B");
        s.runWorker(1000);                   // 상한이 있으므로 반드시 끝난다
    }
}
