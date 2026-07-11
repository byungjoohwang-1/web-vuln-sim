import javax.naming.directory.DirContext;
import javax.naming.directory.SearchControls;

/**
 * [취약 예제] CWE-90 LDAP 삽입 (KISA 1.10)
 *
 * 사용자 입력(uid)을 LDAP 검색 필터 문자열에 그대로 이어붙인다.
 * 공격자가 "*)(uid=*" 같은 값을 넣으면 필터 논리가 변형되어
 * 인증 우회나 디렉터리 전체 열람이 가능해진다.
 */
public class Vulnerable {

    // ctx : 이미 연결된 LDAP 컨텍스트
    public Object searchUser(DirContext ctx, String userInput) throws Exception {
        SearchControls sc = new SearchControls();
        sc.setSearchScope(SearchControls.SUBTREE_SCOPE);

        // ✗ 위험: 사용자 입력을 필터에 문자열 결합
        //   userInput = "*)(uid=*))(|(uid=*" 이면 필터가 깨진다.
        String filter = "(uid=" + userInput + ")";

        // ✗ 위험: 결합된 필터로 그대로 검색 (danger: search(... +)
        return ctx.search("ou=people,dc=example,dc=com", filter, sc);
    }

    public static void main(String[] args) {
        System.out.println("취약 예제: LDAP 필터에 사용자 입력을 직접 결합");
    }
}
