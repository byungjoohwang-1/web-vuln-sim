# 적절하지 않은 난수 값 사용 (Use of Insufficiently Random Values) — CWE-330 / KISA 2.8

## 개념
토큰, 세션 식별자, OTP, 임시 비밀번호처럼 예측 불가능해야 하는 보안값을
예측 가능한 의사난수생성기로 만들어, 공격자가 값을 추측·재현할 수 있는 약점이다.

## 취약 원인
- `java.util.Random`, `Math.random()`은 선형 합동 방식의 의사난수로 보안용이 아니다.
- 시드가 시간 기반이거나 노출되면 이후 출력을 계산할 수 있다.
- 출력값 몇 개만 관찰해도 내부 상태를 역산할 수 있다.

## 공격 시나리오
1. 공격자가 비밀번호 재설정 토큰 몇 개를 관찰해 난수생성기 상태를 역산한다.
2. 다른 사용자에게 발급될 토큰을 미리 예측한다.
3. 예측한 토큰으로 재설정 링크를 가로채 계정을 탈취한다.

## 안전한 코딩
- 보안값은 반드시 `java.security.SecureRandom`(CSPRNG)으로 생성한다.
- 토큰은 충분한 길이(예: 128비트 이상 엔트로피)를 확보한다.
- 예측 가능한 값(시간, 순번, UUIDv1 등)을 보안 토큰으로 사용하지 않는다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable) | 안전(Secure) |
|------|------------------|--------------|
| 난수 생성기 | `new Random()`, `Math.random()` | `SecureRandom` |
| 예측 가능성 | 예측 가능 | 예측 불가 |
| 보안 용도 | 부적합 | 적합 |

## CWE·KISA 매핑
- CWE-330: Use of Insufficiently Random Values
- KISA 소프트웨어 개발보안 가이드(2021.12) 2.8 적절하지 않은 난수 값 사용

## 실행/컴파일 방법
```bash
javac Vulnerable.java && java Vulnerable
javac Secure.java && java Secure
```

## 참고
- CWE-330: https://cwe.mitre.org/data/definitions/330.html
- KISA 소프트웨어 개발보안 가이드(2021.12)
