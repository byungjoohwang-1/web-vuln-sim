/**
 * [취약 예제] Public 메소드로부터 반환된 Private 배열 (CWE-495 / KISA 6.03 캡슐화)
 *
 * 개념:
 *   객체 내부 상태(private 배열)를 public 메소드가 "참조 그대로" 반환하면,
 *   호출자는 캡슐화를 우회해 내부 배열을 직접 수정할 수 있다.
 *   자바 배열은 객체 참조이므로, 반환값을 바꾸면 원본 필드도 함께 바뀐다.
 *
 * 위험 지점:
 *   getScores() 가 this.scores 참조를 그대로 돌려준다.
 *   → 외부에서 반환 배열을 수정하면 내부 불변식이 깨진다.
 */
public class Vulnerable {

    // 내부 상태: 시험 점수 배열 (외부에서 직접 손대면 안 되는 값)
    private int[] scores;

    public Vulnerable(int[] initial) {
        // (별개 약점이지만) 여기서도 방어복사를 하는 것이 이상적이다.
        this.scores = initial;
    }

    /**
     * ★ 취약: private 배열의 참조를 그대로 반환한다.
     *   호출자가 반환값을 수정하면 내부 scores 도 같이 바뀐다(캡슐화 붕괴).
     */
    public int[] getScores() {
        return this.scores;
    }

    public int total() {
        int sum = 0;
        for (int s : scores) sum += s;
        return sum;
    }

    public static void main(String[] args) {
        Vulnerable v = new Vulnerable(new int[]{90, 80, 70});
        System.out.println("합계(정상) = " + v.total()); // 240

        // 외부 코드가 반환 배열을 조작 → 내부 상태 오염
        int[] leaked = v.getScores();
        leaked[0] = 0;

        System.out.println("합계(조작후) = " + v.total()); // 150 — 내부값이 바뀜
    }
}
