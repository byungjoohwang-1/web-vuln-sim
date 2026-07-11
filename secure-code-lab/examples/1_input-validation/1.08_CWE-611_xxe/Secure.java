import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import org.w3c.dom.Document;

/**
 * [안전 예제] XXE 방어 (CWE-611 / KISA 4.8)
 *
 * XML 파서에서 DOCTYPE 선언과 외부 엔티티 처리를 명시적으로 비활성화한다.
 * disallow-doctype-decl 을 켜면 DOCTYPE 자체가 거부되어 XXE 가 원천 차단된다.
 * 추가로 외부 일반/파라미터 엔티티 로딩과 XInclude 도 끈다.
 */
public class Secure {

    static String req() {
        return "<?xml version=\"1.0\"?><r>hello</r>";
    }

    public String parse() throws Exception {
        String xml = req();

        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();

        // ★ 안전: DOCTYPE 선언 자체를 금지 → 외부 엔티티 확장 불가
        factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        // 외부 일반/파라미터 엔티티, XInclude 비활성화
        factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
        factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
        factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
        factory.setXIncludeAware(false);
        factory.setExpandEntityReferences(false);

        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(
                new ByteArrayInputStream(xml.getBytes(StandardCharsets.UTF_8)));
        return doc.getDocumentElement().getTextContent();
    }

    public static void main(String[] args) throws Exception {
        System.out.println(new Secure().parse());
    }
}
