/**
 * [취약 예제] Private 배열에 Public 데이터 할당 (CWE-496 / KISA 6.04 캡슐화)
 *
 * 개념:
 *   외부에서 전달받은 배열 참조를 그대로 private 필드에 저장하면,
 *   호출자가 여전히 그 배열의 참조를 쥐고 있으므로 나중에 외부에서
 *   원소를 바꾸면 객체 내부 상태도 함께 바뀐다.
 *
 * 위험 지점:
 *   setPermissions(int[] p) 가 this.permissions = p 로 참조를 그대로 저장한다.
 *   → 외부 배열을 수정하면 내부 권한 배열이 바뀐다(권한 우회 가능).
 */
public class Vulnerable {

    // 내부 상태: 사용자 권한 코드 배열 (변조되면 안 됨)
    private int[] permissions;

    /**
     * ★ 취약: 외부 배열 참조를 그대로 필드에 저장한다.
     *   호출자가 같은 배열을 계속 조작할 수 있어 내부 상태가 오염된다.
     */
    public void setPermissions(int[] p) {
        this.permissions = p;
    }

    public boolean hasPermission(int code) {
        if (permissions == null) return false;
        for (int c : permissions) {
            if (c == code) return true;
        }
        return false;
    }

    public static void main(String[] args) {
        Vulnerable v = new Vulnerable();

        int[] granted = new int[]{1, 2}; // 1=읽기, 2=쓰기
        v.setPermissions(granted);
        System.out.println("삭제권한(초기) = " + v.hasPermission(9)); // false

        // 외부 코드가 원본 배열을 조작 → 내부 권한이 바뀜
        granted[0] = 9; // 9=삭제 권한 주입
        System.out.println("삭제권한(조작후) = " + v.hasPermission(9)); // true — 권한 우회
    }
}
