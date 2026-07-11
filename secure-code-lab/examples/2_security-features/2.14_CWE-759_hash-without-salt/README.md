# 솔트 없이 일방향 해쉬 함수 사용 (Use of a One-Way Hash without a Salt) — CWE-759 / KISA 2.14

## 개념
비밀번호를 저장할 때 솔트(salt) 없이 단순 해시(SHA-256 등)만 적용하면, 같은 비밀번호는 항상
같은 해시가 된다. 이렇게 되면 미리 계산된 레인보우 테이블로 원문을 역산하기 쉽고, 동일 비밀번호를
쓰는 여러 사용자가 한눈에 드러난다. 빠른 해시 함수는 무차별 대입에도 취약하다.

## 취약 원인
- `MessageDigest.getInstance("SHA-256")` 로 비밀번호를 솔트 없이 한 번만 해싱한다.
- 사용자마다 다른 무작위 값(솔트)을 섞지 않는다.
- 반복(key stretching)이 없어 초당 수억 회 대입이 가능하다.

## 공격 시나리오
1. 공격자가 유출된 사용자 테이블(해시 목록)을 확보한다.
2. 솔트가 없어 사전/레인보우 테이블과 해시를 직접 대조한다.
3. 동일 해시를 가진 계정은 같은 비밀번호임을 즉시 파악한다.
4. 다수 계정의 원문 비밀번호를 짧은 시간에 복구한다.

## 안전한 코딩
- 사용자마다 `SecureRandom` 으로 무작위 솔트를 생성해 함께 저장한다.
- PBKDF2, bcrypt, scrypt, Argon2 같은 느린(반복) 해시를 사용한다.
- 반복 횟수를 충분히 크게 잡아 대입 비용을 높인다.
- 비교는 상수시간(`MessageDigest.isEqual`)으로 수행한다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable) | 안전(Secure) |
|------|------------------|--------------|
| 솔트 | 없음 | `SecureRandom` 무작위 솔트 |
| 알고리즘 | SHA-256 1회 | PBKDF2WithHmacSHA256 반복 |
| 같은 비밀번호 | 항상 같은 해시 | 매번 다른 해시 |
| 무차별 대입 | 매우 빠름 | 반복으로 비용 증가 |

## CWE·KISA 매핑
- CWE-759: Use of a One-Way Hash without a Salt
- KISA 소프트웨어 개발보안 가이드(2021) 보안기능 항목 2.14 솔트 없이 일방향 해쉬 함수 사용

## 실행/컴파일 방법
```bash
javac Vulnerable.java && java Vulnerable
javac Secure.java && java Secure
```

## 참고
- CWE-759 Use of a One-Way Hash without a Salt
- KISA 소프트웨어 개발보안 가이드(2021.12)
- OWASP Password Storage Cheat Sheet
