# 부적절한 전자서명 확인 (Improper Verification of Cryptographic Signature) — CWE-347 / KISA 2.10

## 개념
전자서명은 데이터의 무결성과 발신자 인증을 보장한다. 하지만 서명 검증 API를 호출만 하고
그 결과(성공/실패)를 실제 처리 흐름에 반영하지 않으면, 서명이 위조되어도 정상 데이터처럼
처리된다. 이것이 "부적절한 전자서명 확인" 약점이다.

## 취약 원인
- `Signature.verify()` 가 돌려주는 `boolean` 반환값을 무시하고 버린다.
- 검증 실패 시 예외를 던지거나 요청을 거부하는 분기가 없다.
- "검증 코드가 존재한다"는 사실만으로 안전하다고 착각한다.

## 공격 시나리오
1. 공격자가 메시지를 변조하고 임의의(잘못된) 서명을 붙인다.
2. 서버는 `verify()` 를 호출하지만 반환값을 확인하지 않는다.
3. 검증 실패임에도 이후 로직이 그대로 진행되어 변조 메시지가 신뢰된다.
4. 위조된 명령/거래/업데이트가 그대로 수행된다.

## 안전한 코딩
- `verify()` 의 반환값을 반드시 변수나 조건문으로 확인한다.
- 검증 실패 시 처리를 즉시 중단하고 예외를 던지거나 요청을 거부한다.
- 공개키의 출처(신뢰된 인증서/키스토어)도 함께 검증한다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable) | 안전(Secure) |
|------|------------------|--------------|
| 결과 처리 | `sig.verify(sigBytes);` (버림) | `boolean verified = sig.verify(...)` |
| 실패 대응 | 없음(계속 진행) | `if (verified) {...} else throw` |
| 안전성 | 위조 서명 통과 | 위조 서명 거부 |

## CWE·KISA 매핑
- CWE-347: Improper Verification of Cryptographic Signature
- KISA 소프트웨어 개발보안 가이드(2021) 보안기능 항목 2.10 부적절한 전자서명 확인

## 실행/컴파일 방법
```bash
javac Vulnerable.java && java Vulnerable
javac Secure.java && java Secure
```
(실제 서명/공개키 없이도 컴파일·구조 확인이 가능하도록 작성되어 있다.)

## 참고
- CWE-347 Improper Verification of Cryptographic Signature
- KISA 소프트웨어 개발보안 가이드(2021.12)
- Java `java.security.Signature` API 문서
