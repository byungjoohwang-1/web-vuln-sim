import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

/**
 * [취약 예제] SQL 삽입 (CWE-89 / KISA 4.1)
 *
 * 사용자가 보낸 파라미터(id)를 문자열 연결(+)로 SQL 문장에 그대로 끼워 넣는다.
 * 공격자가 id 값에 따옴표와 논리 연산자를 넣으면 WHERE 조건이 무력화되어
 * 인증 우회, 전체 데이터 유출, 데이터 변조가 가능하다.
 *
 * 위험 지점:
 *   Statement + "SELECT ... = '" + id + "'"  형태의 동적 SQL
 */
public class Vulnerable {

    /** HTTP 요청 파라미터를 흉내내는 헬퍼 (실제로는 request.getParameter). */
    static String req(String name) {
        // 예: id = "' OR '1'='1" 같은 악성 입력이 들어올 수 있다.
        return "' OR '1'='1";
    }

    static Connection getConnection() throws Exception {
        return DriverManager.getConnection("jdbc:h2:mem:test", "sa", "");
    }

    public String findUser() throws Exception {
        String id = req("id"); // 신뢰할 수 없는 외부 입력

        try (Connection conn = getConnection()) {
            // ★ 취약: 외부 입력을 문자열 연결로 SQL에 직접 삽입한다.
            //   따옴표 하나만으로도 쿼리 구조가 통째로 바뀔 수 있다.
            Statement stmt = conn.createStatement();
            String sql = "SELECT name FROM members WHERE user_id = '" + id + "'";
            ResultSet rs = stmt.executeQuery("SELECT name FROM members WHERE user_id = '" + id + "'");
            if (rs.next()) {
                return rs.getString("name");
            }
            return null;
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println(new Vulnerable().findUser());
    }
}
