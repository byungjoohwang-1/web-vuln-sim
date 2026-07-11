import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import org.w3c.dom.Document;

/**
 * [취약 예제] 부적절한 XML 외부개체 참조 (XXE) (CWE-611 / KISA 4.8)
 *
 * 기본 설정 그대로의 XML 파서는 DOCTYPE 내 외부 엔티티(&xxe;)를 확장한다.
 * 공격자가 외부 엔티티로 로컬 파일을 참조하면 파일 내용이 유출되거나
 * SSRF, 서비스 거부(DoS)로 이어질 수 있다.
 *
 * 위험 지점:
 *   DocumentBuilderFactory 를 보안 기능 설정 없이 그대로 사용
 */
public class Vulnerable {

    /** 외부에서 들어온 XML 흉내. 실제로는 요청 본문. */
    static String req() {
        return "<?xml version=\"1.0\"?>"
             + "<!DOCTYPE r [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>"
             + "<r>&xxe;</r>";
    }

    public String parse() throws Exception {
        String xml = req();

        // ★ 취약: 외부 엔티티/DOCTYPE 차단 설정을 하지 않았다.
        //   &xxe; 가 확장되어 /etc/passwd 내용이 파싱 결과에 포함될 수 있다.
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(
                new ByteArrayInputStream(xml.getBytes(StandardCharsets.UTF_8)));
        return doc.getDocumentElement().getTextContent();
    }

    public static void main(String[] args) throws Exception {
        System.out.println(new Vulnerable().parse());
    }
}
