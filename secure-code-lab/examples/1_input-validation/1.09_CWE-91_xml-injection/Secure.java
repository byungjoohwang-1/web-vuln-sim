/**
 * [안전 예제] XML 삽입 방어 (CWE-91 / KISA 4.9)
 *
 * XML 문서에 값을 넣기 전에 특수문자를 XML 엔티티로 이스케이프한다(escapeXml).
 * < > & " ' 를 엔티티로 변환하면 입력이 텍스트 데이터로만 취급되어
 * 태그를 주입해도 XML 구조가 바뀌지 않는다.
 * (운영에서는 DOM setTextContent 또는 StringEscapeUtils.escapeXml 권장)
 */
public class Secure {

    static String req(String name) {
        return "guest</role><role>admin"; // 악성 입력이 와도 이스케이프로 무력화
    }

    /** XML 특수문자 이스케이프 (escapeXml). */
    static String escapeXml(String s) {
        if (s == null) return "";
        return s.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
                .replace("'", "&apos;");
    }

    public String buildProfileXml() {
        String name = req("name");
        String role = "user";

        // ★ 안전: 값을 XML에 넣기 전에 이스케이프한다. 태그 주입이 무력화된다.
        String xml = "<profile>"
                   + "<name>" + escapeXml(name) + "</name>"
                   + "<role>" + escapeXml(role) + "</role>"
                   + "</profile>";
        return xml;
    }

    public static void main(String[] args) {
        System.out.println(new Secure().buildProfileXml());
    }
}
