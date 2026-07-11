import javax.servlet.http.Cookie;

/**
 * [취약 예제] 하드디스크 저장 쿠키를 통한 정보 노출 (CWE-539 / KISA 2.12)
 *
 * 인증 토큰(민감정보)을 브라우저 디스크에 장기간 남는 영속 쿠키로 저장한다.
 * setMaxAge를 큰 양수(예: 3600초, 혹은 하루)로 지정하면 브라우저가 쿠키를
 * 디스크에 파일로 저장한다. 공유 PC에서는 브라우저를 닫아도 토큰이 남아
 * 다음 사용자나 로컬 접근자가 세션을 탈취할 수 있다.
 *
 * 위험 지점:
 *   cookie.setMaxAge(3600);   // 영속 쿠키 → 디스크에 저장됨
 */
public class Vulnerable {

    /**
     * 로그인 성공 후 인증 토큰을 쿠키로 내려준다.
     * ★ 취약: 민감한 토큰을 만료시간이 긴 영속 쿠키로 저장하고
     *   HttpOnly/Secure 플래그도 설정하지 않는다.
     */
    public Cookie issueAuthCookie(String authToken) {
        Cookie cookie = new Cookie("AUTH", authToken);
        cookie.setPath("/");
        // ★ 취약: 1시간짜리 영속 쿠키. 브라우저가 디스크에 저장한다.
        cookie.setMaxAge(3600);
        return cookie;
    }

    public static void main(String[] args) {
        System.out.println("취약 예제: 민감정보를 영속 쿠키(디스크 저장)로 내려준다.");
    }
}
