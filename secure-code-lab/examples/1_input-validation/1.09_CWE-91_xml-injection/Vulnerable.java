/**
 * [취약 예제] XML 삽입 (XML Injection) (CWE-91 / KISA 4.9)
 *
 * 외부 입력을 문자열 연결로 XML 문서에 그대로 끼워 넣는다.
 * 공격자가 태그(<, >)나 새로운 요소를 입력에 넣으면 XML 구조가 바뀌어
 * 데이터 위조, 권한 상승(예: <role>admin</role> 주입)이 가능하다.
 *
 * 위험 지점:
 *   "<name>" + input + "</name>"  형태의 XML 문자열 조립
 */
public class Vulnerable {

    /** HTTP 요청 파라미터 흉내 헬퍼. */
    static String req(String name) {
        // 예: name = "guest</role><role>admin"
        return "hong";
    }

    public String buildProfileXml() {
        String name = req("name");   // 신뢰할 수 없는 외부 입력
        String role = "user";

        // ★ 취약: 입력을 XML에 문자열로 직접 삽입한다. 태그가 그대로 문법이 된다.
        //   name 에 "</name><role>admin" 을 넣으면 role 요소가 위조된다.
        String xml = "<profile>"
                   + "<name>" + name + "</name>"
                   + "<role>" + role + "</role>"
                   + "</profile>";
        return xml;
    }

    public static void main(String[] args) {
        System.out.println(new Vulnerable().buildProfileXml());
    }
}
