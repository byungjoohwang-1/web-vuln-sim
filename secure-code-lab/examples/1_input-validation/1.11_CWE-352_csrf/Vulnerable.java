import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * [취약 예제] CWE-352 크로스사이트 요청 위조 (KISA 1.11)
 *
 * 상태를 변경하는 POST 요청을 처리하면서 요청의 출처를 전혀 검증하지 않는다.
 * 세션 쿠키만 신뢰하므로, 로그인된 피해자가 공격자가 만든 페이지를
 * 방문하면 브라우저가 자동으로 쿠키를 실어 위조 요청을 전송한다.
 */
public class Vulnerable extends HttpServlet {

    // ✗ 위험: 출처 검증 토큰 없이 계좌이체 같은 상태변경을 수행 (danger: doPost()
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws java.io.IOException {

        String to = request.getParameter("to");
        String amount = request.getParameter("amount");

        // ✗ 위험: 세션 존재만 확인하고 요청 진위(고유 토큰)는 확인하지 않는다.
        Object user = request.getSession().getAttribute("loginUser");
        if (user != null) {
            transfer(user.toString(), to, amount);   // 위조 요청도 그대로 실행
            response.getWriter().write("transfer done");
        }
    }

    private void transfer(String from, String to, String amount) {
        System.out.println(from + " -> " + to + " : " + amount);
    }

    public static void main(String[] args) {
        System.out.println("취약 예제: 요청 진위 토큰 없이 상태변경 POST 처리");
    }
}
