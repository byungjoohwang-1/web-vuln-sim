import java.util.Arrays;
import java.util.logging.Logger;

/**
 * [안전 예제] Private 배열에 Public 데이터 안전 할당 (CWE-496 / KISA 6.04 캡슐화)
 *
 * 안전한 코딩:
 *   외부에서 받은 배열은 참조를 저장하지 말고, 방어적 복사본을 저장한다.
 *   - this.arr = p.clone(); 또는 Arrays.copyOf(p, p.length);
 *   그러면 호출자가 원본 배열을 나중에 수정해도 내부 상태는 안전하다.
 */
public class Secure {

    private static final Logger LOG = Logger.getLogger(Secure.class.getName());

    private int[] permissions;

    /**
     * ★ 안전: 입력 배열을 복사해 저장한다.
     *   외부에서 원본 배열을 조작해도 this.permissions 는 영향을 받지 않는다.
     */
    public void setPermissions(int[] p) {
        this.permissions = (p == null) ? new int[0] : p.clone();
    }

    /** 조회 시에도 복사본을 반환해 유출을 막는다(CWE-495 동반 방어). */
    public int[] getPermissions() {
        return Arrays.copyOf(permissions, permissions.length);
    }

    public boolean hasPermission(int code) {
        if (permissions == null) return false;
        for (int c : permissions) {
            if (c == code) return true;
        }
        return false;
    }

    public static void main(String[] args) {
        Secure s = new Secure();

        int[] granted = new int[]{1, 2};
        s.setPermissions(granted);
        LOG.info("삭제권한(초기) = " + s.hasPermission(9)); // false

        // 외부 코드가 원본을 조작해도 내부는 안전
        granted[0] = 9;
        LOG.info("삭제권한(조작시도후) = " + s.hasPermission(9)); // false — 우회 불가
    }
}
