# 적절한 인증 없는 중요기능 허용 (Missing Authentication) — CWE-306 / KISA 2.1

## 개념
중요기능(관리 작업, 개인정보 조회, 금액 이동 등)을 수행하는 요청 처리부에서
사용자의 인증 여부를 확인하지 않아, 인증되지 않은 사용자가 그대로 기능을
실행할 수 있는 약점이다. 로그인 화면만 있고 실제 서버 로직에서 인증을 다시
확인하지 않으면, 공격자는 화면을 우회해 엔드포인트를 직접 호출한다.

## 취약 원인
- `doGet`/`doPost` 같은 요청 진입점에서 세션·토큰·권한 검사를 생략한다.
- "화면에서 이미 걸렀으니 서버는 믿어도 된다"는 잘못된 전제.
- 인증 검사를 클라이언트(JS, 화면 노출 여부)에만 의존한다.

## 공격 시나리오
1. 공격자가 관리자 페이지의 폼 action URL(예: `/admin/point`)을 알아낸다.
2. 로그인 없이 해당 URL로 직접 POST 요청을 보낸다.
3. 서버가 인증을 확인하지 않으므로 "전 회원 포인트 지급"이 그대로 실행된다.

## 안전한 코딩
- 모든 중요기능 진입점에서 서버 세션으로 인증을 재확인한다.
- `request.getSession(false)`로 기존 세션만 조회하고, 없으면 미인증으로 처리한다.
- `session.getAttribute("user")`로 로그인 상태를, 필요한 경우 권한(role)까지 확인한다.
- 프레임워크 사용 시 `@PreAuthorize`, 인터셉터/필터로 공통 인증을 강제한다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable) | 안전(Secure) |
|------|------------------|--------------|
| 인증 확인 | 없음 | `getSession(false)` + `getAttribute("user")` |
| 권한 확인 | 없음 | `role == ADMIN` 확인 |
| 미인증 요청 | 그대로 실행 | 401/403으로 거부 |

## CWE·KISA 매핑
- CWE-306: Missing Authentication for Critical Function
- KISA 소프트웨어 개발보안 가이드(2021) 2.1 적절한 인증 없는 중요기능 허용

## 실행/컴파일 방법
```bash
javac Vulnerable.java && java Vulnerable
javac Secure.java && java Secure
```

## 참고
- CWE-306: https://cwe.mitre.org/data/definitions/306.html
- KISA 소프트웨어 개발보안 가이드(2021.12)
