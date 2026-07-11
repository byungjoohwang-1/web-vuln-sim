import java.util.HashMap;
import java.util.Map;

/**
 * [취약 예제] Null Pointer 역참조 (CWE-476 / KISA 5.01)
 *
 * request.getParameter("keyword") 는 해당 파라미터가 없으면 null 을 돌려준다.
 * 그런데 반환값에 대한 null 검사 없이 곧바로 .trim() 을 호출한다.
 * 파라미터가 누락되면 NullPointerException 이 발생해 요청 처리가 중단된다.
 *
 * 위험 지점:
 *   getParameter("keyword").trim()  ← null 가능 값을 곧바로 역참조
 */
public class Vulnerable {

    /** 서블릿 request.getParameter 를 흉내내는 간단한 요청 객체. */
    static class Request {
        private final Map<String, String> params = new HashMap<>();
        String getParameter(String name) {
            // 파라미터가 없으면 null 을 반환한다 (서블릿과 동일한 동작).
            return params.get(name);
        }
    }

    public String normalizeKeyword(Request request) {
        // ★ 취약: getParameter 반환값이 null 인지 확인하지 않고 바로 메서드를 호출한다.
        //   keyword 파라미터가 없으면 이 줄에서 NullPointerException 이 터진다.
        String keyword = request.getParameter("keyword").trim().toLowerCase();
        return keyword;
    }

    public static void main(String[] args) {
        // 데모: keyword 파라미터를 넣지 않은 빈 요청 → null 역참조로 예외 발생.
        Request req = new Request();
        System.out.println(new Vulnerable().normalizeKeyword(req));
    }
}
