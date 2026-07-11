/**
 * [취약 예제] 취약한 API 사용 (CWE-676 / KISA 7.02 API 오용)
 *
 * 개념:
 *   설계상 위험하거나 폐기(deprecated)된 API 를 사용하면 데이터 손상,
 *   상태 불일치, 이식성 문제를 일으킨다.
 *
 * 위험 지점 1:
 *   String.getBytes() 를 문자셋 없이 호출 → 플랫폼 기본 인코딩에 의존.
 *   서버/PC 마다 결과 바이트가 달라져 해시·서명·전송 데이터가 깨진다.
 *
 * 위험 지점 2:
 *   Thread.stop() 은 폐기된 API 로, 스레드를 강제 종료하며 잠금/불변식을
 *   깨뜨려 객체를 손상된 상태로 남긴다.
 */
public class Vulnerable {

    /** ★ 취약: 문자셋 미지정 getBytes() — 플랫폼 기본 인코딩에 의존해 결과가 달라진다. */
    public byte[] encode(String message) {
        return message.getBytes();
    }

    /** ★ 취약: Thread.stop() 은 폐기된 위험 API — 데이터 손상 위험. */
    @SuppressWarnings("deprecation")
    public void forceKill(Thread worker) {
        worker.stop();
    }

    public static void main(String[] args) {
        Vulnerable v = new Vulnerable();
        byte[] bytes = v.encode("안녕하세요");
        System.out.println("byte length = " + bytes.length); // 플랫폼마다 다를 수 있음
    }
}
