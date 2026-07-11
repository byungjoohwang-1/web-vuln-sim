import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

/**
 * [안전 예제] Null Pointer 역참조 방지 (CWE-476 / KISA 5.01)
 *
 * getParameter 반환값을 역참조하기 전에 반드시 null 여부를 확인한다.
 * 여기서는 두 가지 방어를 함께 보여준다.
 *   1) 명시적 null 검사 (!= null) 후 기본값 대체
 *   2) Objects.requireNonNull 로 계약을 문서화하는 방법(참고)
 */
public class Secure {

    /** 서블릿 request.getParameter 를 흉내내는 간단한 요청 객체. */
    static class Request {
        private final Map<String, String> params = new HashMap<>();
        String getParameter(String name) {
            return params.get(name);
        }
    }

    public String normalizeKeyword(Request request) {
        String raw = request.getParameter("keyword");

        // ★ 안전: 역참조 전에 null 을 확인한다. null 이면 안전한 기본값으로 대체한다.
        if (raw == null) {
            return "";
        }
        return raw.trim().toLowerCase();
    }

    /** 반드시 값이 있어야 하는 필수 파라미터는 계약을 명시해 조기 실패시킨다. */
    public String requireKeyword(Request request) {
        String raw = Objects.requireNonNull(
                request.getParameter("keyword"), "keyword 파라미터는 필수입니다");
        return raw.trim().toLowerCase();
    }

    public static void main(String[] args) {
        Request req = new Request();
        // keyword 가 없어도 예외 없이 빈 문자열을 안전하게 반환한다.
        System.out.println("[" + new Secure().normalizeKeyword(req) + "]");
    }
}
