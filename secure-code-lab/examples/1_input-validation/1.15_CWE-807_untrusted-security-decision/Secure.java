import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * [안전 예제] CWE-807 방어 (KISA 1.15)
 *
 * 권한은 클라이언트 입력이 아니라 서버가 관리하는 세션/저장소에서 읽는다.
 * 로그인 시 서버가 검증한 role 을 세션에 저장했고, 인가 판단은 그 값으로만
 * 수행한다. 클라이언트는 이 값을 조작할 수 없다.
 */
public class Secure {

    public void deleteUser(HttpServletRequest request, HttpServletResponse response)
            throws java.io.IOException {

        // ✓ 안전: 권한은 server-side 세션에서만 조회한다.
        String role = (String) request.getSession().getAttribute("role");

        if ("admin".equals(role)) {
            // 삭제 대상 식별자는 데이터로만 취급(보안 결정 아님)
            String targetId = request.getParameter("targetId");
            doDelete(targetId);
            response.getWriter().write("deleted " + targetId);
        } else {
            response.sendError(HttpServletResponse.SC_FORBIDDEN);
        }
    }

    private void doDelete(String id) {
        System.out.println("delete user " + id);
    }

    public static void main(String[] args) {
        System.out.println("안전 예제: 세션(server-side)에서 role 을 읽어 인가 판단");
    }
}
