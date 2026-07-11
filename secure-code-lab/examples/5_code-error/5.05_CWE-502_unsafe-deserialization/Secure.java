import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.ObjectInputFilter;
import java.io.ObjectInputStream;

/**
 * [안전 예제] 역직렬화 화이트리스트 필터 (CWE-502 / KISA 5.05)
 *
 * ObjectInputStream 에 ObjectInputFilter(허용 클래스 화이트리스트)를 설정한다.
 * 복원이 허용된 클래스만 통과시키고, 그 외 클래스는 거부(REJECTED)한다.
 * 또한 그래프 깊이/참조 수 한도를 두어 자원 고갈 공격도 막는다.
 *
 * 더 근본적인 대안:
 *   가능하면 자바 네이티브 직렬화를 쓰지 말고 JSON 등 데이터 포맷 +
 *   스키마 검증(예: Jackson readValue + 타입 제한)을 사용한다.
 *
 * 안전 지점:
 *   ois.setObjectInputFilter(allowList)  ← 허용 클래스만 역직렬화
 */
public class Secure {

    // ★ 안전: 역직렬화를 허용할 클래스만 명시한 ALLOWLIST 필터.
    private static final ObjectInputFilter ALLOWLIST = ObjectInputFilter.Config.createFilter(
            "java.lang.String;java.lang.Number;java.util.ArrayList;"
                    + "maxdepth=5;maxrefs=100;!*"); // 나머지 전부 거부

    public Object load(byte[] untrusted) throws IOException, ClassNotFoundException {
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(untrusted));
        // 역직렬화 전에 화이트리스트 필터를 적용한다.
        ois.setObjectInputFilter(ALLOWLIST);
        return ois.readObject();
    }

    public static void main(String[] args) throws Exception {
        byte[] data = new byte[0];
        System.out.println(new Secure().load(data));
    }
}
