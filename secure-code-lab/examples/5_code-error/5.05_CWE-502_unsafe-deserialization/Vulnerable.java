import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.ObjectInputStream;

/**
 * [취약 예제] 신뢰할 수 없는 데이터의 역직렬화 (CWE-502 / KISA 5.05)
 *
 * 외부에서 받은 바이트 배열을 아무런 검증 없이 ObjectInputStream.readObject()
 * 로 역직렬화한다. 자바 네이티브 역직렬화는 스트림에 기술된 임의 클래스의
 * 객체를 복원하며, 이 과정에서 readObject/readResolve 등이 실행된다.
 * 공격자가 가젯 체인(예: Commons-Collections)을 담은 스트림을 보내면
 * 원격 코드 실행(RCE)까지 이어질 수 있다.
 *
 * 위험 지점:
 *   new ObjectInputStream(...).readObject()  ← 필터 없는 무제한 역직렬화
 */
public class Vulnerable {

    public Object load(byte[] untrusted) throws IOException, ClassNotFoundException {
        // ★ 취약: 어떤 클래스가 복원될지 통제하지 않는다.
        //   신뢰 경계를 넘어온 바이트를 그대로 객체로 되살린다.
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(untrusted));
        return ois.readObject();
    }

    public static void main(String[] args) throws Exception {
        // 실제로는 네트워크/파일에서 온 바이트가 들어온다.
        byte[] data = new byte[0];
        System.out.println(new Vulnerable().load(data));
    }
}
