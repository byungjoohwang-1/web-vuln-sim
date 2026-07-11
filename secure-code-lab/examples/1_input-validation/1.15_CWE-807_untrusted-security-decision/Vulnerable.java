import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * [취약 예제] CWE-807 보안기능 결정에 사용되는 부적절한 입력값 (KISA 1.15)
 *
 * 권한(role)을 클라이언트가 보낸 요청 파라미터에서 읽어 보안 결정을 내린다.
 * 클라이언트는 파라미터를 임의로 조작할 수 있으므로, 일반 사용자도
 * role=admin 을 보내기만 하면 관리자 기능에 접근할 수 있다.
 */
public class Vulnerable {

    public void deleteUser(HttpServletRequest request, HttpServletResponse response)
            throws java.io.IOException {

        // ✗ 위험: 신뢰할 수 없는 클라이언트 입력으로 권한 판단 (danger: getParameter("role")
        String role = request.getParameter("role");

        if ("admin".equals(role)) {
            String targetId = request.getParameter("targetId");
            doDelete(targetId);                     // 누구나 role=admin 이면 통과
            response.getWriter().write("deleted " + targetId);
        } else {
            response.sendError(HttpServletResponse.SC_FORBIDDEN);
        }
    }

    private void doDelete(String id) {
        System.out.println("delete user " + id);
    }

    public static void main(String[] args) {
        System.out.println("취약 예제: 클라이언트가 보낸 role 로 인가 판단");
    }
}
