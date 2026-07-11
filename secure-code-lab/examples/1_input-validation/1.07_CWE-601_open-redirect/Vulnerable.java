/**
 * [취약 예제] 신뢰되지 않는 URL 자동접속 연결 (Open Redirect) (CWE-601 / KISA 4.7)
 *
 * 외부 입력(url 파라미터)을 검증 없이 리다이렉트 대상으로 사용한다.
 * 공격자가 신뢰된 도메인 링크에 외부 악성 URL을 실어 보내면,
 * 사용자는 정상 사이트를 거쳐 피싱 사이트로 이동하게 된다.
 *
 * 위험 지점:
 *   response.sendRedirect(request.getParameter("url"))
 */
public class Vulnerable {

    /** HttpServletRequest 흉내 목(mock). */
    static class Request {
        String getParameter(String name) {
            // 예: url = "http://evil-phishing.example/login"
            return "/mypage";
        }
    }

    /** HttpServletResponse 흉내 목(mock). */
    static class Response {
        void sendRedirect(String location) {
            System.out.println("Location: " + location);
        }
    }

    public void handleLogin(Request request, Response response) {
        // ★ 취약: 외부에서 받은 URL을 그대로 리다이렉트 대상으로 사용한다.
        //   외부 절대 URL(http://evil...)도 그대로 통과한다.
        response.sendRedirect(request.getParameter("url"));
    }

    public static void main(String[] args) {
        new Vulnerable().handleLogin(new Request(), new Response());
    }
}
