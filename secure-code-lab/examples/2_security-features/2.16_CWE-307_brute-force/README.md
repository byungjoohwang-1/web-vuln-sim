# 반복된 인증시도 제한 기능 부재 (Improper Restriction of Excessive Authentication Attempts) — CWE-307 / KISA 2.16

## 개념
로그인 같은 인증 절차에 실패 횟수 제한·계정 잠금·지연 같은 억제 장치가 없으면,
공격자는 같은 계정에 대해 무한히 비밀번호를 자동 시도(무차별 대입)할 수 있다.
"반복된 인증시도 제한 기능 부재"는 약한 비밀번호(2.09)와 결합하면 계정 탈취로 직결된다.

## 취약 원인
- 로그인 실패 횟수를 세지 않고, 임계치 도달 시 잠그지 않는다.
- 실패 후 지연(back-off)이나 CAPTCHA 같은 억제 수단이 없다.
- 동일 IP/계정의 폭주 요청을 제한(RateLimiter)하지 않는다.

## 공격 시나리오
1. 공격자가 대상 계정 ID를 확보한다.
2. 자동화 도구로 초당 수백~수천 건의 비밀번호를 반복 시도한다.
3. 시도 제한이 없어 사전/무차별 대입이 끝까지 진행된다.
4. 결국 올바른 비밀번호를 찾아 계정을 탈취한다.

## 안전한 코딩
- 계정별 실패 횟수(`failCount`)를 누적하고, 임계치를 넘으면 일정 시간 잠근다(`isLocked`).
- 잠금 시간 동안은 올바른 비밀번호라도 즉시 거부한다.
- 성공 시 카운터를 초기화한다.
- IP 기준 RateLimiter, 지수 지연, CAPTCHA, 이상 로그인 알림을 함께 적용한다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable) | 안전(Secure) |
|------|------------------|--------------|
| 실패 추적 | 없음 | `failCount` 로 누적 |
| 계정 잠금 | 없음 | 임계치 초과 시 `isLocked` |
| 무차별 대입 | 무제한 가능 | 임계치 이후 차단 |

## CWE·KISA 매핑
- CWE-307: Improper Restriction of Excessive Authentication Attempts
- KISA 소프트웨어 개발보안 가이드(2021) 보안기능 항목 2.16 반복된 인증시도 제한 기능 부재

## 실행/컴파일 방법
```bash
javac Vulnerable.java && java Vulnerable
javac Secure.java && java Secure
```

## 참고
- CWE-307 Improper Restriction of Excessive Authentication Attempts
- KISA 소프트웨어 개발보안 가이드(2021.12)
- OWASP Authentication Cheat Sheet (Account Lockout)
