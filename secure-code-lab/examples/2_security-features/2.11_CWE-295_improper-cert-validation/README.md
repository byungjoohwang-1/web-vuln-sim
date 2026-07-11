# 부적절한 인증서 유효성 검증 (Improper Certificate Validation) — CWE-295 / KISA 2.11

## 개념
TLS/SSL 통신에서 서버 인증서를 제대로 검증하지 않으면, 통신 상대가 진짜 서버인지 보장할 수 없다.
인증서 체인·유효기간·호스트 이름을 검증하지 않는 "Trust-All" 구현은 중간자 공격(MITM)에
그대로 노출된다. 이것이 "부적절한 인증서 유효성 검증" 약점이다.

## 취약 원인
- `X509TrustManager.checkServerTrusted()` 본문을 비워 모든 인증서를 신뢰한다.
- 호스트 이름 검증기를 항상 `true` 를 반환하도록 만든다(`ALLOW_ALL_HOSTNAME_VERIFIER`).
- 인증서 유효기간(`checkValidity`)이나 신뢰 저장소(PKIX) 검증을 생략한다.
- 개발 편의(자가서명 인증서 회피)로 넣은 코드를 운영에 그대로 남긴다.

## 공격 시나리오
1. 공격자가 클라이언트와 서버 사이에 위치한다(공용 Wi-Fi, DNS 스푸핑 등).
2. 공격자가 자신의 위조 인증서를 제시한다.
3. 클라이언트가 인증서를 검증하지 않아 위조 인증서를 신뢰한다.
4. 공격자는 트래픽을 복호화·변조하며 자격증명과 데이터를 탈취한다.

## 안전한 코딩
- 시스템 신뢰 저장소(cacerts) 기반의 표준 `TrustManagerFactory` 를 사용한다.
- 인증서 체인을 PKIX 규칙(`PKIXParameters`, `CertPathValidator`)으로 검증한다.
- 각 인증서의 `checkValidity()` 로 유효기간을 확인한다.
- 호스트 이름 검증은 기본 검증기(`getDefaultHostnameVerifier`)에 위임한다.
- 커스텀 TrustManager로 검증을 비활성화하지 않는다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable) | 안전(Secure) |
|------|------------------|--------------|
| 체인 검증 | `checkServerTrusted(...) {}` (없음) | PKIX + TrustManagerFactory |
| 유효기간 | 확인 안 함 | `cert.checkValidity()` |
| 호스트명 | 무조건 통과 | `getDefaultHostnameVerifier().verify(...)` |

## CWE·KISA 매핑
- CWE-295: Improper Certificate Validation
- KISA 소프트웨어 개발보안 가이드(2021) 보안기능 항목 2.11 부적절한 인증서 유효성 검증

## 실행/컴파일 방법
```bash
javac Vulnerable.java && java Vulnerable
javac Secure.java && java Secure
```

## 참고
- CWE-295 Improper Certificate Validation
- KISA 소프트웨어 개발보안 가이드(2021.12)
- Java `javax.net.ssl`, `java.security.cert` API 문서
