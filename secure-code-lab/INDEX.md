# Secure Code Lab — 49개 보안약점 색인

KISA 『소프트웨어 개발보안 가이드(2021)』 구현단계 보안약점 49종. 각 항목은 취약/안전 코드 쌍과 설명(README)을 포함한다.

## 입력검증 및 표현  (17)

| 번호 | CWE | 약점 | 언어 | 심각도 | 폴더 |
|---|---|---|---|---|---|
| 1.01 | CWE-89 | SQL 삽입 | JAVA | High | [`sql-injection`](examples/1_input-validation/1.01_CWE-89_sql-injection/) |
| 1.02 | CWE-94 | 코드 삽입 | JAVA | High | [`code-injection`](examples/1_input-validation/1.02_CWE-94_code-injection/) |
| 1.03 | CWE-22 | 경로 조작 및 자원 삽입 | JAVA | High | [`path-traversal`](examples/1_input-validation/1.03_CWE-22_path-traversal/) |
| 1.04 | CWE-79 | 크로스사이트 스크립트(XSS) | JAVA | High | [`xss`](examples/1_input-validation/1.04_CWE-79_xss/) |
| 1.05 | CWE-78 | 운영체제 명령어 삽입 | JAVA | High | [`os-command-injection`](examples/1_input-validation/1.05_CWE-78_os-command-injection/) |
| 1.06 | CWE-434 | 위험한 형식 파일 업로드 | JAVA | High | [`file-upload`](examples/1_input-validation/1.06_CWE-434_file-upload/) |
| 1.07 | CWE-601 | 신뢰되지 않는 URL 자동접속 연결 | JAVA | Medium | [`open-redirect`](examples/1_input-validation/1.07_CWE-601_open-redirect/) |
| 1.08 | CWE-611 | 부적절한 XML 외부개체 참조 | JAVA | High | [`xxe`](examples/1_input-validation/1.08_CWE-611_xxe/) |
| 1.09 | CWE-91 | XML 삽입 | JAVA | Medium | [`xml-injection`](examples/1_input-validation/1.09_CWE-91_xml-injection/) |
| 1.10 | CWE-90 | LDAP 삽입 | JAVA | High | [`ldap-injection`](examples/1_input-validation/1.10_CWE-90_ldap-injection/) |
| 1.11 | CWE-352 | 크로스사이트 요청 위조(CSRF) | JAVA | High | [`csrf`](examples/1_input-validation/1.11_CWE-352_csrf/) |
| 1.12 | CWE-918 | 서버사이드 요청 위조(SSRF) | JAVA | High | [`ssrf`](examples/1_input-validation/1.12_CWE-918_ssrf/) |
| 1.13 | CWE-113 | HTTP 응답분할 | JAVA | Medium | [`http-response-splitting`](examples/1_input-validation/1.13_CWE-113_http-response-splitting/) |
| 1.14 | CWE-190 | 정수형 오버플로우 | C | High | [`integer-overflow`](examples/1_input-validation/1.14_CWE-190_integer-overflow/) |
| 1.15 | CWE-807 | 보안기능 결정에 사용되는 부적절한 입력값 | JAVA | High | [`untrusted-security-decision`](examples/1_input-validation/1.15_CWE-807_untrusted-security-decision/) |
| 1.16 | CWE-120 | 메모리 버퍼 오버플로우 | C | High | [`buffer-overflow`](examples/1_input-validation/1.16_CWE-120_buffer-overflow/) |
| 1.17 | CWE-134 | 포맷 스트링 삽입 | C | High | [`format-string`](examples/1_input-validation/1.17_CWE-134_format-string/) |

## 보안기능  (16)

| 번호 | CWE | 약점 | 언어 | 심각도 | 폴더 |
|---|---|---|---|---|---|
| 2.01 | CWE-306 | 적절한 인증 없는 중요기능 허용 | JAVA | High | [`missing-authentication`](examples/2_security-features/2.01_CWE-306_missing-authentication/) |
| 2.02 | CWE-285 | 부적절한 인가 | JAVA | High | [`improper-authorization`](examples/2_security-features/2.02_CWE-285_improper-authorization/) |
| 2.03 | CWE-732 | 중요자원에 대한 잘못된 권한 설정 | JAVA | Medium | [`incorrect-permission`](examples/2_security-features/2.03_CWE-732_incorrect-permission/) |
| 2.04 | CWE-327 | 취약한 암호화 알고리즘 사용 | JAVA | High | [`weak-crypto`](examples/2_security-features/2.04_CWE-327_weak-crypto/) |
| 2.05 | CWE-311 | 암호화되지 않은 중요정보 | JAVA | High | [`missing-encryption`](examples/2_security-features/2.05_CWE-311_missing-encryption/) |
| 2.06 | CWE-798 | 하드코드된 중요정보 | JAVA | High | [`hardcoded-credentials`](examples/2_security-features/2.06_CWE-798_hardcoded-credentials/) |
| 2.07 | CWE-326 | 충분하지 않은 키 길이 사용 | JAVA | High | [`weak-key-length`](examples/2_security-features/2.07_CWE-326_weak-key-length/) |
| 2.08 | CWE-330 | 적절하지 않은 난수 값 사용 | JAVA | Medium | [`weak-random`](examples/2_security-features/2.08_CWE-330_weak-random/) |
| 2.09 | CWE-521 | 취약한 비밀번호 허용 | JAVA | Medium | [`weak-password`](examples/2_security-features/2.09_CWE-521_weak-password/) |
| 2.10 | CWE-347 | 부적절한 전자서명 확인 | JAVA | High | [`improper-signature-verification`](examples/2_security-features/2.10_CWE-347_improper-signature-verification/) |
| 2.11 | CWE-295 | 부적절한 인증서 유효성 검증 | JAVA | High | [`improper-cert-validation`](examples/2_security-features/2.11_CWE-295_improper-cert-validation/) |
| 2.12 | CWE-539 | 하드디스크 저장 쿠키를 통한 정보 노출 | JAVA | Medium | [`sensitive-cookie`](examples/2_security-features/2.12_CWE-539_sensitive-cookie/) |
| 2.13 | CWE-615 | 주석문 안에 포함된 시스템 주요정보 | JAVA | Low | [`info-in-comments`](examples/2_security-features/2.13_CWE-615_info-in-comments/) |
| 2.14 | CWE-759 | 솔트 없이 일방향 해쉬 함수 사용 | JAVA | Medium | [`hash-without-salt`](examples/2_security-features/2.14_CWE-759_hash-without-salt/) |
| 2.15 | CWE-494 | 무결성 검사 없는 코드 다운로드 | JAVA | High | [`code-download-integrity`](examples/2_security-features/2.15_CWE-494_code-download-integrity/) |
| 2.16 | CWE-307 | 반복된 인증시도 제한 기능 부재 | JAVA | Medium | [`brute-force`](examples/2_security-features/2.16_CWE-307_brute-force/) |

## 시간 및 상태  (2)

| 번호 | CWE | 약점 | 언어 | 심각도 | 폴더 |
|---|---|---|---|---|---|
| 3.01 | CWE-367 | 경쟁조건: 검사시점과 사용시점(TOCTOU) | JAVA | Medium | [`toctou`](examples/3_time-and-state/3.01_CWE-367_toctou/) |
| 3.02 | CWE-835 | 종료되지 않는 반복문 또는 재귀 함수 | JAVA | Medium | [`infinite-loop`](examples/3_time-and-state/3.02_CWE-835_infinite-loop/) |

## 에러처리  (3)

| 번호 | CWE | 약점 | 언어 | 심각도 | 폴더 |
|---|---|---|---|---|---|
| 4.01 | CWE-209 | 오류 메시지 정보노출 | JAVA | Medium | [`error-message-leak`](examples/4_error-handling/4.01_CWE-209_error-message-leak/) |
| 4.02 | CWE-391 | 오류상황 대응 부재 | JAVA | Medium | [`unchecked-error`](examples/4_error-handling/4.02_CWE-391_unchecked-error/) |
| 4.03 | CWE-755 | 부적절한 예외 처리 | JAVA | Medium | [`improper-exception`](examples/4_error-handling/4.03_CWE-755_improper-exception/) |

## 코드오류  (5)

| 번호 | CWE | 약점 | 언어 | 심각도 | 폴더 |
|---|---|---|---|---|---|
| 5.01 | CWE-476 | Null Pointer 역참조 | JAVA | Medium | [`null-pointer-dereference`](examples/5_code-error/5.01_CWE-476_null-pointer-dereference/) |
| 5.02 | CWE-404 | 부적절한 자원 해제 | JAVA | Medium | [`resource-leak`](examples/5_code-error/5.02_CWE-404_resource-leak/) |
| 5.03 | CWE-416 | 해제된 자원 사용 | C | High | [`use-after-free`](examples/5_code-error/5.03_CWE-416_use-after-free/) |
| 5.04 | CWE-457 | 초기화되지 않은 변수 사용 | C | Medium | [`uninitialized-variable`](examples/5_code-error/5.04_CWE-457_uninitialized-variable/) |
| 5.05 | CWE-502 | 신뢰할 수 없는 데이터의 역직렬화 | JAVA | High | [`unsafe-deserialization`](examples/5_code-error/5.05_CWE-502_unsafe-deserialization/) |

## 캡슐화  (4)

| 번호 | CWE | 약점 | 언어 | 심각도 | 폴더 |
|---|---|---|---|---|---|
| 6.01 | CWE-488 | 잘못된 세션에 의한 데이터 정보 노출 | JAVA | Medium | [`wrong-session-data`](examples/6_encapsulation/6.01_CWE-488_wrong-session-data/) |
| 6.02 | CWE-489 | 제거되지 않고 남은 디버그 코드 | JAVA | Low | [`debug-code`](examples/6_encapsulation/6.02_CWE-489_debug-code/) |
| 6.03 | CWE-495 | Public 메소드로부터 반환된 Private 배열 | JAVA | Low | [`private-array-return`](examples/6_encapsulation/6.03_CWE-495_private-array-return/) |
| 6.04 | CWE-496 | Private 배열에 Public 데이터 할당 | JAVA | Low | [`public-to-private-array`](examples/6_encapsulation/6.04_CWE-496_public-to-private-array/) |

## API 오용  (2)

| 번호 | CWE | 약점 | 언어 | 심각도 | 폴더 |
|---|---|---|---|---|---|
| 7.01 | CWE-350 | DNS lookup에 의존한 보안결정 | JAVA | Medium | [`dns-security-decision`](examples/7_api-abuse/7.01_CWE-350_dns-security-decision/) |
| 7.02 | CWE-676 | 취약한 API 사용 | JAVA | Medium | [`dangerous-api`](examples/7_api-abuse/7.02_CWE-676_dangerous-api/) |

**합계: 49개 약점**