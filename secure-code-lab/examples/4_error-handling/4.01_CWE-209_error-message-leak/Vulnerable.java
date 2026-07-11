import java.io.IOException;
import java.io.PrintWriter;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * [취약 예제] 오류 메시지 정보노출 (CWE-209 / KISA 에러처리)
 *
 * 내부 예외의 상세 정보(스택 트레이스, 예외 메시지)를 그대로
 * HTTP 응답으로 사용자에게 노출한다. 이 정보에는 DB 종류, 테이블/컬럼명,
 * 파일 경로, 내부 클래스 구조 등이 담겨 공격자에게 정찰 단서를 준다.
 *
 * 위험 지점:
 *   e.printStackTrace()  + response 로 e.getMessage() 직접 출력
 */
public class Vulnerable extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws IOException {
        PrintWriter out = response.getWriter();
        try {
            String idText = request.getParameter("id");
            int id = Integer.parseInt(idText);      // 잘못된 입력이면 예외
            out.println("조회 결과 id=" + lookup(id));
        } catch (Exception e) {
            // ★ 취약 1: 콘솔에 전체 스택 트레이스를 그대로 찍는다.
            e.printStackTrace();
            // ★ 취약 2: 내부 예외 메시지를 응답으로 사용자에게 노출한다.
            out.println("오류가 발생했습니다: " + e.getMessage());
            out.println(e.toString());
        }
    }

    private String lookup(int id) {
        if (id < 0) {
            // 내부 구현 세부가 메시지에 그대로 드러난다.
            throw new IllegalStateException(
                "SELECT * FROM secret_members WHERE seq=" + id + " (DB=oracle11g)");
        }
        return "member#" + id;
    }
}
