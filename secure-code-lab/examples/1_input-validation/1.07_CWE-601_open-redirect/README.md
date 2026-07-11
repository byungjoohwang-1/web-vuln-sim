# 신뢰되지 않는 URL 자동접속 연결 (Open Redirect) · CWE-601 · KISA 4.7

## 개념
Open Redirect는 애플리케이션이 외부 입력을 검증 없이 리다이렉트 목적지로 사용할 때, 공격자가 신뢰된 도메인을 경유해 사용자를 임의 외부 사이트로 유도하는 약점이다. 피싱·인증정보 탈취에 악용된다.

## 취약 원인
- `sendRedirect(request.getParameter("url"))` 처럼 입력을 그대로 이동 대상으로 사용했다.
- 외부 절대 URL(`http://`, `//host`)을 걸러내지 않았다.
- 허용 목적지 목록을 두지 않았다.

## 공격 시나리오
- `https://trusted.site/go?url=http://evil-phish/login` 링크를 배포해 정상 사이트처럼 위장한다.
- `//evil.example` (스킴 상대 URL)로 검증을 우회한다.
- OAuth 콜백 리다이렉트를 조작해 토큰을 탈취한다.

## 안전한 코딩(핵심 조치)
- 허용된 목적지 화이트리스트(`ALLOWLIST`)에서만 이동 대상을 고른다.
- 외부 절대 URL을 차단하고 내부 경로(`/`로 시작, `//` 제외)만 허용한다.
- 이동 대상을 직접 노출하지 말고 서버가 관리하는 키→URL 매핑을 쓴다.
- 부득이 외부 이동 시 경고 페이지를 거친다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 대상 선택 | 입력 그대로 | `ALLOWLIST` 검증 |
| 외부 URL | 통과 | `startsWith("/")` + `//` 차단 |
| 기본값 | 없음 | 안전한 기본 경로 |

## CWE·KISA 매핑
- CWE-601: URL Redirection to Untrusted Site ('Open Redirect')
- KISA 소프트웨어 개발보안 가이드(2021) 4장 입력검증 및 표현 — 신뢰되지 않는 URL 자동접속 연결

## 실행/컴파일 방법
```
javac Vulnerable.java
javac Secure.java

python bugfinder/bugfinder.py examples/1_input-validation/1.07_CWE-601_open-redirect
```

## 참고
- CWE-601: https://cwe.mitre.org/data/definitions/601.html
- OWASP Unvalidated Redirects and Forwards Cheat Sheet
