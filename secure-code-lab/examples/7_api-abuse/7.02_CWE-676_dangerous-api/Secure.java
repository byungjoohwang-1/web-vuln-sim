import java.nio.charset.StandardCharsets;
import java.util.logging.Logger;

/**
 * [안전 예제] 안전한 API 사용 (CWE-676 / KISA 7.02 API 오용)
 *
 * 안전한 코딩:
 *   - 문자 → 바이트 변환은 항상 명시적 문자셋을 지정한다:
 *       message.getBytes(StandardCharsets.UTF_8)
 *     플랫폼 기본 인코딩에 의존하지 않아 결과가 결정적이다.
 *   - 스레드는 강제 종료(Thread.stop) 대신 협력적 중단(interrupt + 플래그)으로
 *     안전하게 정리한다.
 */
public class Secure {

    private static final Logger LOG = Logger.getLogger(Secure.class.getName());

    /** ★ 안전: 명시적 UTF-8 인코딩으로 결정적인 바이트 결과를 얻는다. */
    public byte[] encode(String message) {
        return message.getBytes(StandardCharsets.UTF_8);
    }

    /** ★ 안전: 강제 종료 대신 interrupt 신호로 협력적 중단을 요청한다. */
    public void requestStop(Thread worker) {
        worker.interrupt();
    }

    /** 협력적 중단을 존중하는 작업 스레드 예시. */
    static class Worker implements Runnable {
        @Override
        public void run() {
            while (!Thread.currentThread().isInterrupted()) {
                // ... 작업 수행 ...
            }
            // 루프를 빠져나오며 자원을 안전하게 정리한다.
        }
    }

    public static void main(String[] args) throws InterruptedException {
        Secure s = new Secure();
        byte[] bytes = s.encode("안녕하세요");
        LOG.info("byte length = " + bytes.length); // 어디서 실행하든 동일(UTF-8)

        Thread t = new Thread(new Worker());
        t.start();
        s.requestStop(t);
        t.join();
    }
}
