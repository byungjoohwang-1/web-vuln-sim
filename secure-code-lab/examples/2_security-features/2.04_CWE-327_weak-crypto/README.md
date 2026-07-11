# 취약한 암호화 알고리즘 사용 (Use of a Broken/Risky Cryptographic Algorithm) — CWE-327 / KISA 2.4

## 개념
안전하지 않다고 알려진 암호 알고리즘·모드(DES, RC4, MD5, SHA-1, ECB 등)를
사용해, 암호화했음에도 기밀성·무결성이 실제로는 보장되지 않는 약점이다.

## 취약 원인
- DES(56비트)처럼 키 공간이 작아 전수조사가 가능한 알고리즘 사용.
- ECB 모드는 같은 평문 블록이 같은 암호문이 되어 패턴이 노출된다.
- MD5/SHA-1은 충돌이 발견되어 서명·무결성 용도로 부적합하다.

## 공격 시나리오
1. DES로 암호화된 데이터를 확보한 공격자가 GPU/전용 하드웨어로 키를 전수조사한다.
2. ECB로 암호화된 이미지/구조화 데이터에서 반복 패턴을 읽어 정보를 추정한다.
3. MD5 해시로 무결성을 검증하는 시스템에 충돌 쌍을 이용한 위조 파일을 제출한다.

## 안전한 코딩
- 대칭키 암호는 AES(128비트 이상, 권장 256비트)를 사용한다.
- 운영 모드는 GCM 같은 AEAD를 사용해 기밀성과 무결성을 함께 얻는다.
- 해시는 SHA-256 이상을 사용하고, 비밀번호는 PBKDF2/bcrypt/Argon2를 쓴다.
- IV/nonce는 매번 안전한 난수로 새로 생성한다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable) | 안전(Secure) |
|------|------------------|--------------|
| 대칭키 알고리즘 | DES/ECB | AES-256/GCM |
| 해시 | MD5 | SHA-256 |
| 무결성 보장 | 없음 | GCM(AEAD)로 제공 |

## CWE·KISA 매핑
- CWE-327: Use of a Broken or Risky Cryptographic Algorithm
- KISA 소프트웨어 개발보안 가이드(2021.12) 2.4 취약한 암호화 알고리즘 사용

## 실행/컴파일 방법
```bash
javac Vulnerable.java && java Vulnerable
javac Secure.java && java Secure
```

## 참고
- CWE-327: https://cwe.mitre.org/data/definitions/327.html
- KISA 소프트웨어 개발보안 가이드(2021.12)
