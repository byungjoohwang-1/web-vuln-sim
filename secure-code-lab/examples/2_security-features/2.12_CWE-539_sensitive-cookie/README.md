# 하드디스크 저장 쿠키를 통한 정보 노출 (Use of Persistent Cookies Containing Sensitive Information) — CWE-539 / KISA 2.12

## 개념
쿠키의 만료시간(`Max-Age`/`Expires`)을 설정하면 브라우저는 그 쿠키를 디스크에 파일로 저장한다
(영속 쿠키). 인증 토큰·세션 식별자 같은 민감정보를 영속 쿠키로 내려주면, 브라우저를 닫아도
디스크에 남아 공유 PC나 로컬 접근자가 이를 훔쳐 세션을 탈취할 수 있다.

## 취약 원인
- 민감정보를 담은 쿠키에 `setMaxAge(양수)` 를 지정해 디스크에 영속 저장한다.
- `HttpOnly`, `Secure` 플래그를 설정하지 않아 스크립트 접근·평문 전송에 노출된다.
- 서버 세션에 두어야 할 값을 클라이언트 쿠키에 그대로 담는다.

## 공격 시나리오
1. 사용자가 공용/공유 PC에서 로그인한다.
2. 서버가 인증 토큰을 1시간짜리 영속 쿠키로 내려준다.
3. 사용자가 브라우저를 닫아도 쿠키 파일이 디스크에 남는다.
4. 다음 사용자가 그 파일을 읽거나 재사용해 이전 사용자의 세션을 탈취한다.

## 안전한 코딩
- 민감정보의 실제 값은 서버측 세션(`getSession`)에 저장한다.
- 클라이언트에는 세션 식별자만 담되, 세션 쿠키(`setMaxAge(-1)` 또는 미지정)로 만들어
  브라우저 종료 시 사라지게 한다.
- `setHttpOnly(true)` 로 스크립트 접근을 막고 `setSecure(true)` 로 HTTPS 전송만 허용한다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable) | 안전(Secure) |
|------|------------------|--------------|
| 저장 위치 | 쿠키에 민감정보 직접 | 서버 세션에 보관 |
| 만료 | `setMaxAge(3600)` (디스크 저장) | `setMaxAge(-1)` (세션 쿠키) |
| 플래그 | 없음 | `HttpOnly`, `Secure` |

## CWE·KISA 매핑
- CWE-539: Use of Persistent Cookies Containing Sensitive Information
- KISA 소프트웨어 개발보안 가이드(2021) 보안기능 항목 2.12 하드디스크 저장 쿠키를 통한 정보 노출

## 실행/컴파일 방법
`javax.servlet` API가 필요하다(서블릿 컨테이너 또는 servlet-api.jar).
```bash
javac -cp servlet-api.jar Vulnerable.java
javac -cp servlet-api.jar Secure.java
```

## 참고
- CWE-539 Use of Persistent Cookies Containing Sensitive Information
- KISA 소프트웨어 개발보안 가이드(2021.12)
- OWASP Session Management Cheat Sheet
