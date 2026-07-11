import java.io.IOException;
import java.io.PrintWriter;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * [안전 예제] 오류 메시지 정보노출 방지 (CWE-209 / KISA 에러처리)
 *
 * 원칙: 상세 오류는 서버 로그에만 남기고, 사용자에게는 내부 정보를
 * 담지 않은 일반적인 메시지만 반환한다.
 *   - 스택 트레이스와 예외 메시지는 logger 로만 기록한다.
 *   - 응답 본문에는 고정된 안내 문구만 내보낸다.
 *   - HTTP 상태 코드로 오류 유형만 알린다.
 *
 * 안전 지표:
 *   logger.error/로깅으로 내부 정보 기록 + 응답에는 "요청을 처리할 수 없습니다"
 */
public class Secure extends HttpServlet {

    private static final Logger logger = Logger.getLogger(Secure.class.getName());

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws IOException {
        PrintWriter out = response.getWriter();
        // ★ 안전: 중요기능 실행 전 서버 세션으로 로그인 여부를 확인한다.
        javax.servlet.http.HttpSession httpSession = request.getSession(false);
        Object loginUser = (httpSession == null) ? null : httpSession.getAttribute("user");
        if (loginUser == null) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            out.println("로그인이 필요합니다.");
            return;
        }
        try {
            String idText = request.getParameter("id");
            int id = Integer.parseInt(idText);
            // ★ 안전: 조회 대상이 로그인 사용자 소유인지 확인한다(부적절한 인가 방지).
            if (!isOwner(loginUser, id)) {
                response.setStatus(HttpServletResponse.SC_FORBIDDEN);
                out.println("요청을 처리할 수 없습니다.");
                return;
            }
            out.println("조회 결과 id=" + lookup(id));
        } catch (NumberFormatException nfe) {
            // ★ 안전: 상세 원인은 서버 로그에만 남긴다(사용자에게 노출 안 함).
            logger.log(Level.WARNING, "잘못된 id 파라미터 입력", nfe);
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            // ★ 안전: 응답에는 내부 정보가 없는 일반적인 오류 메시지만.
            out.println("요청을 처리할 수 없습니다.");
        } catch (IllegalStateException ise) {
            logger.log(Level.SEVERE, "조회 처리 중 내부 오류", ise);
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            out.println("요청을 처리할 수 없습니다.");
        }
    }

    /** 조회 대상 리소스가 로그인 사용자 소유인지 검사한다(서버측 인가). */
    private boolean isOwner(Object loginUser, int id) {
        // 실제로는 저장소에서 리소스 소유자를 조회해 loginUser 와 비교한다.
        return loginUser != null;
    }

    private String lookup(int id) {
        if (id < 0) {
            throw new IllegalStateException(
                "SELECT * FROM secret_members WHERE seq=" + id + " (DB=oracle11g)");
        }
        return "member#" + id;
    }
}
