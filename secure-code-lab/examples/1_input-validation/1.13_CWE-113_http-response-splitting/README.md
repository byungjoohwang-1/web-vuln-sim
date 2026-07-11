## HTTP 응답분할 (HTTP Response Splitting) — CWE-113 / KISA 1.13

## 개념
HTTP 응답분할은 사용자 입력에 포함된 CR(`\r`, %0d)·LF(`\n`, %0a)를 걸러내지 않고 응답 헤더에 넣을 때 발생한다. 개행문자는 헤더의 경계이므로, 주입되면 공격자가 임의 헤더나 두 번째 응답(본문)을 만들어 캐시 오염, 세션 고정, 반사형 XSS로 확장할 수 있다.

## 취약 원인
- `response.addHeader(name, request.getParameter(...))`처럼 사용자 입력을 헤더 값에 직접 넣는다.
- CR/LF 및 제어문자를 제거하거나 거부하지 않는다.
- `Location`, `Set-Cookie` 등 민감 헤더에도 필터 없이 값을 사용한다.

## 공격 시나리오
1. 언어 설정 파라미터 `lang`에 `ko%0d%0aSet-Cookie:%20sid=attacker`를 넣는다.
2. 서버가 이를 그대로 헤더에 반영하면 응답에 공격자가 지정한 `Set-Cookie`가 삽입된다.
3. 나아가 `%0d%0a%0d%0a<script>...`로 본문을 붙여 반사형 XSS나 캐시 포이즈닝을 유발한다.

## 안전한 코딩
- 헤더에 넣기 전 CR/LF(`[\r\n]`)와 제어문자를 제거하거나, 포함 시 요청을 거부한다.
- 값에 화이트리스트 정규식(`matches`)을 적용해 허용된 형식만 통과시킨다.
- 최신 서블릿 컨테이너의 헤더 정규화 기능을 신뢰하되, 애플리케이션에서도 방어한다.
- 리다이렉트 대상은 화이트리스트와 함께 다룬다(오픈 리다이렉트도 함께 예방).

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable.java) | 안전(Secure.java) |
|------|----------------------|-------------------|
| CRLF 처리 | 없음 | stripCrlf로 제거 |
| 형식 검증 | 없음 | matches 화이트리스트 |
| 헤더 주입 | 가능 | 불가 |

## CWE·KISA 매핑
- CWE-113: Improper Neutralization of CRLF Sequences in HTTP Headers
- KISA 소프트웨어 개발보안 가이드(2021) 입력검증 및 표현 — 1.13 HTTP 응답분할

## 실행/컴파일 방법
서블릿 API가 필요하다.
```
javac -cp servlet-api.jar Vulnerable.java Secure.java
java Secure   # stripCrlf 동작 확인
```
버그 파인더 검증:
```
python bugfinder/bugfinder.py examples/1_input-validation/1.13_CWE-113_http-response-splitting
```

## 참고
- CWE-113 (MITRE)
- OWASP HTTP Response Splitting
- 소프트웨어 개발보안 가이드(2021) 1.13
