import java.util.Arrays;
import java.util.logging.Logger;

/**
 * [안전 예제] Private 배열의 안전한 반환 (CWE-495 / KISA 6.03 캡슐화)
 *
 * 안전한 코딩:
 *   내부 배열을 외부로 넘길 때는 참조가 아니라 "방어적 복사본"을 반환한다.
 *   - 배열: this.arr.clone() 또는 Arrays.copyOf(...)
 *   - 컬렉션: Collections.unmodifiableList(...) 등 불변 뷰
 *   호출자가 복사본을 아무리 수정해도 내부 상태는 안전하다.
 */
public class Secure {

    private static final Logger LOG = Logger.getLogger(Secure.class.getName());

    private int[] scores;

    public Secure(int[] initial) {
        // 생성 시에도 방어적 복사로 외부 참조와 끊는다.
        this.scores = Arrays.copyOf(initial, initial.length);
    }

    /**
     * ★ 안전: 내부 배열의 복사본을 반환한다.
     *   반환값을 외부에서 수정해도 this.scores 는 영향을 받지 않는다.
     */
    public int[] getScores() {
        return this.scores.clone();
    }

    public int total() {
        int sum = 0;
        for (int s : scores) sum += s;
        return sum;
    }

    public static void main(String[] args) {
        Secure s = new Secure(new int[]{90, 80, 70});
        LOG.info("합계(정상) = " + s.total()); // 240

        // 외부 코드가 반환 배열을 조작해도 내부는 안전
        int[] copy = s.getScores();
        copy[0] = 0;

        LOG.info("합계(조작시도후) = " + s.total()); // 240 — 그대로 유지
    }
}
