import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

/**
 * [안전 예제] SQL 삽입 방어 (CWE-89 / KISA 4.1)
 *
 * PreparedStatement + 파라미터 바인딩(setString)을 사용한다.
 * 사용자 입력은 SQL '데이터'로만 취급되고 '코드'로 해석되지 않으므로,
 * 따옴표나 논리 연산자를 넣어도 쿼리 구조가 바뀌지 않는다.
 */
public class Secure {

    static String req(String name) {
        return "' OR '1'='1"; // 악성 입력이 와도 파라미터 바인딩이 무력화한다.
    }

    static Connection getConnection() throws Exception {
        return DriverManager.getConnection("jdbc:h2:mem:test", "sa", "");
    }

    public String findUser() throws Exception {
        String id = req("id");

        try (Connection conn = getConnection()) {
            // ★ 안전: 쿼리 골격을 먼저 고정하고 값은 ? 자리표시자로 바인딩한다.
            String sql = "SELECT name FROM members WHERE user_id = ?";
            try (PreparedStatement ps = conn.prepareStatement(sql)) {
                ps.setString(1, id); // 입력을 순수 데이터로 바인딩
                try (ResultSet rs = ps.executeQuery()) {
                    if (rs.next()) {
                        return rs.getString("name");
                    }
                    return null;
                }
            }
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println(new Secure().findUser());
    }
}
