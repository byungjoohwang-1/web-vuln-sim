import javax.naming.directory.DirContext;
import javax.naming.directory.SearchControls;

/**
 * [안전 예제] CWE-90 LDAP 삽입 방어 (KISA 1.10)
 *
 * 사용자 입력을 LDAP 특수문자 이스케이프(escapeFilter) 후에만 필터에 사용한다.
 * RFC 4515가 규정하는 * ( ) \ NUL 등을 백슬래시-16진 형태로 치환하면
 * 입력이 필터 논리를 바꾸지 못한다.
 */
public class Secure {

    /**
     * LDAP 검색 필터용 이스케이프 (OWASP ESAPI encodeForLDAP와 동일한 원리).
     * escapeFilter : 필터 메타문자를 무력화한다.
     */
    public static String escapeFilter(String input) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < input.length(); i++) {
            char c = input.charAt(i);
            switch (c) {
                case '\\': sb.append("\\5c"); break;
                case '*':  sb.append("\\2a"); break;
                case '(':  sb.append("\\28"); break;
                case ')':  sb.append("\\29"); break;
                case '\0': sb.append("\\00"); break;
                default:   sb.append(c);
            }
        }
        return sb.toString();
    }

    public Object searchUser(DirContext ctx, String userInput) throws Exception {
        SearchControls sc = new SearchControls();
        sc.setSearchScope(SearchControls.SUBTREE_SCOPE);

        // ✓ 안전: 먼저 이스케이프한 값만 필터 인자로 사용한다.
        String safe = escapeFilter(userInput);
        String filter = "(uid={0})";

        // 이스케이프된 값을 filter arguments 로 전달 (문자열 결합 아님)
        return ctx.search("ou=people,dc=example,dc=com", filter,
                new Object[]{ safe }, sc);
    }

    public static void main(String[] args) {
        System.out.println("안전 예제 escapeFilter: " + escapeFilter("*)(uid=*"));
    }
}
