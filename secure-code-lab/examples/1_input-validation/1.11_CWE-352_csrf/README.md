## 크로스사이트 요청 위조 (CSRF) — CWE-352 / KISA 1.11

## 개념
CSRF는 인증된 사용자의 브라우저가 공격자의 의도대로 위조 요청을 전송하게 만드는 공격이다. 브라우저는 대상 사이트의 세션 쿠키를 자동으로 실어 보내므로, 서버가 "요청의 진위"를 별도로 검증하지 않으면 피해자 권한으로 상태변경(이체, 비밀번호 변경 등)이 실행된다.

## 취약 원인
- 상태를 변경하는 POST 요청에서 세션 쿠키(로그인 여부)만 신뢰한다.
- 요청마다 검증할 예측 불가능한 CSRF 토큰이 없다.
- 쿠키에 SameSite 속성이 없어 교차 사이트 요청에도 쿠키가 전송된다.

## 공격 시나리오
1. 피해자가 은행 사이트에 로그인한 상태(세션 쿠키 보유)를 유지한다.
2. 공격자가 만든 페이지에 자동 제출되는 폼 `<form action="/transfer" method="POST">`을 심는다.
3. 피해자가 그 페이지를 열면 브라우저가 세션 쿠키와 함께 `/transfer`로 POST를 보낸다.
4. 서버는 토큰 검증이 없어 정상 요청으로 처리하고 공격자 계좌로 이체한다.

## 안전한 코딩
- 동기화 토큰 패턴: 세션에 난수 토큰을 저장하고 폼 hidden 필드로 내려보낸 뒤, 요청 시 세션 토큰과 비교한다.
- 프레임워크의 CSRF 보호(Spring Security CSRF 필터 등)를 활성화한다.
- 세션 쿠키에 `SameSite=Strict`(또는 Lax), `HttpOnly`, `Secure`를 적용한다.
- 중요한 작업은 재인증(비밀번호 재입력)을 요구한다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable.java) | 안전(Secure.java) |
|------|----------------------|-------------------|
| 요청 진위 | 검증 없음 | 세션 토큰과 `_token` 비교 |
| 쿠키 속성 | SameSite 없음 | SameSite=Strict 적용 |
| 위조 요청 | 그대로 실행 | 403으로 거부 |

## CWE·KISA 매핑
- CWE-352: Cross-Site Request Forgery (CSRF)
- KISA 소프트웨어 개발보안 가이드(2021) 입력검증 및 표현 — 1.11 크로스사이트 요청 위조

## 실행/컴파일 방법
서블릿 API(`javax.servlet`)가 필요하다.
```
javac -cp servlet-api.jar Vulnerable.java Secure.java
```
버그 파인더 검증:
```
python bugfinder/bugfinder.py examples/1_input-validation/1.11_CWE-352_csrf
```

## 참고
- CWE-352 (MITRE)
- OWASP CSRF Prevention Cheat Sheet
- 소프트웨어 개발보안 가이드(2021) 1.11
