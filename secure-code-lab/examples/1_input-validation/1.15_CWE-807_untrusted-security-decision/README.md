## 보안기능 결정에 사용되는 부적절한 입력값 — CWE-807 / KISA 1.15

## 개념
CWE-807은 인증·인가·가격 결정 같은 보안 판단을 클라이언트가 조작할 수 있는 입력값(요청 파라미터, 헤더, 쿠키, hidden 필드)에 의존할 때 발생한다. 클라이언트가 보낸 값은 신뢰 경계 밖에 있으므로, 이를 근거로 권한을 부여하면 누구나 값을 바꿔 통제를 우회할 수 있다.

## 취약 원인
- `request.getParameter("role")`처럼 권한/등급/금액을 클라이언트 입력에서 읽는다.
- 서버가 관리하는 신뢰 가능한 출처(세션, DB)와 대조하지 않는다.
- hidden 필드나 헤더의 값을 검증 없이 보안 결정에 사용한다.

## 공격 시나리오
1. 관리자 삭제 API가 `role` 파라미터로 권한을 판단한다.
2. 일반 사용자가 요청에 `role=admin`을 추가로 붙여 전송한다.
3. 서버가 그 값을 그대로 신뢰해 관리자 기능(사용자 삭제)을 수행한다.
4. 마찬가지로 `price=0`, `amount=-100` 같은 조작으로 결제/포인트 로직도 우회된다.

## 안전한 코딩
- 권한·가격 등 보안 결정값은 반드시 서버측 출처(세션 속성, 저장소 조회)에서 가져온다.
- 로그인 시 서버가 검증한 role을 세션에 저장하고, 인가 판단은 그 값으로만 한다.
- 금액/가격은 서버 DB의 기준값(`repository`, `findBy...`)으로 재계산한다.
- 클라이언트 입력은 "데이터"로만 취급하고 "결정 근거"로 삼지 않는다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable.java) | 안전(Secure.java) |
|------|----------------------|-------------------|
| 권한 출처 | `getParameter("role")` | `getSession().getAttribute("role")` |
| 신뢰 경계 | 클라이언트(조작 가능) | 서버(조작 불가) |
| 결과 | 권한 상승 | 정당한 인가만 허용 |

## CWE·KISA 매핑
- CWE-807: Reliance on Untrusted Inputs in a Security Decision
- KISA 소프트웨어 개발보안 가이드(2021) 입력검증 및 표현 — 1.15 보안기능 결정에 사용되는 부적절한 입력값

## 실행/컴파일 방법
서블릿 API가 필요하다.
```
javac -cp servlet-api.jar Vulnerable.java Secure.java
```
버그 파인더 검증:
```
python bugfinder/bugfinder.py examples/1_input-validation/1.15_CWE-807_untrusted-security-decision
```

## 참고
- CWE-807 (MITRE)
- OWASP Broken Access Control
- 소프트웨어 개발보안 가이드(2021) 1.15
