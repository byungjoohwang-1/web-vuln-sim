import java.util.Set;

/**
 * [안전 예제] Open Redirect 방어 (CWE-601 / KISA 4.7)
 *
 * 외부 URL을 그대로 쓰지 않는다. 허용된 목적지 화이트리스트(ALLOWLIST)에서만
 * 선택하거나, 외부 절대 URL을 차단하고 자기 사이트 내부 경로(/로 시작)만 허용한다.
 */
public class Secure {

    static class Request {
        String getParameter(String name) { return "/mypage"; }
    }

    static class Response {
        void sendRedirect(String location) { System.out.println("Location: " + location); }
    }

    // 허용된 이동 목적지 화이트리스트
    private static final Set<String> ALLOWLIST = Set.of("/mypage", "/dashboard", "/orders");
    private static final String DEFAULT = "/home";

    public void handleLogin(Request request, Response response) {
        String requested = request.getParameter("url");

        // ★ 안전: 허용목록에 있는 값만 사용. 외부 절대 URL(//, http)은 거부한다.
        String target = DEFAULT;
        if (requested != null
                && requested.startsWith("/")
                && !requested.startsWith("//")
                && ALLOWLIST.contains(requested)) {
            target = requested;
        }

        response.sendRedirect(target);
    }

    public static void main(String[] args) {
        new Secure().handleLogin(new Request(), new Response());
    }
}
