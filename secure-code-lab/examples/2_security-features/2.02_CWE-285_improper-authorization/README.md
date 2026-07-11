# 부적절한 인가 (Improper Authorization) — CWE-285 / KISA 2.2

## 개념
인증(누구인지 확인)은 통과했지만 인가(무엇을 할 수 있는지 확인)를 제대로 하지
않아, 사용자가 자신의 권한을 넘어서는 자원에 접근할 수 있는 약점이다.
대표적으로 식별자만 바꿔 남의 데이터를 조회/수정하는 IDOR가 있다.

## 취약 원인
- 요청 파라미터로 받은 자원 식별자(id, accountId 등)를 소유자 검증 없이 사용한다.
- "로그인만 했으면 이 자원에 접근해도 된다"는 잘못된 전제.
- 접근 통제를 목록 화면(내 것만 보임)에만 의존하고 실제 조회 API에서 확인하지 않는다.

## 공격 시나리오
1. alice가 로그인해 자신의 계좌 조회 요청 `accountId=A-1001`을 관찰한다.
2. 값을 `A-2002`로 바꿔 재전송한다.
3. 서버가 소유자 검증을 하지 않으므로 bob의 계좌 잔액이 그대로 노출된다.

## 안전한 코딩
- 자원 접근 전, 서버가 보관한 소유자 정보와 로그인 사용자를 비교한다.
- `isOwner(accountId, loginUser)`처럼 소유·권한 검증을 통과한 경우에만 반환한다.
- 역할 기반 접근제어(`hasRole`)나 `@PreAuthorize`로 공통 인가 정책을 강제한다.
- 식별자는 예측 불가능한 값(UUID 등)으로 두고, 그래도 서버측 검증을 생략하지 않는다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable) | 안전(Secure) |
|------|------------------|--------------|
| 소유자 검증 | 없음 | `isOwner` + `ownerId.equals(loginUser)` |
| 남의 자원 접근 | 가능(IDOR) | 거부(SecurityException) |
| 신뢰 기준 | 요청 파라미터 | 서버측 소유자 데이터 |

## CWE·KISA 매핑
- CWE-285: Improper Authorization
- KISA 소프트웨어 개발보안 가이드(2021.12) 2.2 부적절한 인가

## 실행/컴파일 방법
```bash
javac Vulnerable.java && java Vulnerable
javac Secure.java && java Secure
```

## 참고
- CWE-285: https://cwe.mitre.org/data/definitions/285.html
- KISA 소프트웨어 개발보안 가이드(2021.12)
