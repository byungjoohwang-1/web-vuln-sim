import java.io.PrintWriter;

/**
 * [안전 예제] XSS 방어 (CWE-79 / KISA 4.4)
 *
 * 출력 문맥(HTML)에 맞게 입력을 이스케이프한 뒤 응답에 넣는다.
 * < > & " ' 를 HTML 엔티티로 변환하면 <script> 가 텍스트로만 표시되고
 * 코드로 실행되지 않는다. (운영에서는 OWASP Encoder/StringEscapeUtils 권장)
 */
public class Secure {

    static class Request {
        String getParameter(String name) {
            return "<script>alert(1)</script>";
        }
    }

    /** HTML 특수문자 이스케이프 (escapeHtml). */
    static String escapeHtml(String s) {
        if (s == null) return "";
        return s.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
                .replace("'", "&#x27;");
    }

    public void render(Request request, PrintWriter out) {
        String keyword = request.getParameter("keyword");

        // ★ 안전: HTML 문맥에 넣기 전에 이스케이프한다. 태그가 실행되지 않는다.
        out.println("<div>검색어: " + escapeHtml(keyword) + "</div>");
        out.print("<p>" + escapeHtml(keyword) + "</p>");
    }

    public static void main(String[] args) {
        new Secure().render(new Request(), new PrintWriter(System.out, true));
    }
}
