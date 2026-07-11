# 취약한 API 사용 (CWE-676 / KISA 7.02 API 오용)

## 제목
- 약점명: 취약한 API 사용 (위험 함수 사용)
- CWE: CWE-676 (Use of Potentially Dangerous Function)
- KISA 개발보안 가이드(2021) 항목: 7.02 (API 오용)

## 개념
설계상 위험하거나 폐기(deprecated)된 API 를 사용하면 데이터 손상, 상태
불일치, 이식성 문제를 유발한다. 안전한 대체 API 가 존재한다면 그것을 써야 한다.

## 취약 원인
- `String.getBytes()` 를 문자셋 없이 호출 → 플랫폼 기본 인코딩에 의존해 결과 바이트가 환경마다 달라진다(해시·서명·전송 손상).
- `Thread.stop()` 은 폐기된 API 로, 스레드를 강제 종료하며 잠금/불변식을 깨뜨려 객체를 손상된 상태로 남긴다.

## 영향
- 인코딩 불일치로 데이터 무결성·서명 검증 실패.
- 강제 종료로 인한 자원 누수, 락 미해제, 데이터 손상.

## 안전한 코딩
- 문자 → 바이트 변환은 명시적 문자셋을 지정한다: `getBytes(StandardCharsets.UTF_8)`.
- 스레드 종료는 강제 중단 대신 협력적 중단(`interrupt()` + `isInterrupted()` 체크)으로 처리한다.
- 폐기 API 는 컴파일 경고를 확인하고 안전한 대체 API 로 교체한다.

## 취약 vs 안전 차이
- 취약: `message.getBytes()`, `worker.stop()`.
- 안전: `message.getBytes(StandardCharsets.UTF_8)`, `worker.interrupt()`.

## CWE·KISA 매핑
- CWE-676: Use of Potentially Dangerous Function
- KISA 개발보안 가이드(2021) 7.02 API 오용 — 취약한 API 사용

## 실행/컴파일 방법
```bash
javac Vulnerable.java Secure.java
java Vulnerable   # 플랫폼 기본 인코딩 의존 / 폐기 API 사용
java Secure       # UTF-8 명시 + 협력적 스레드 중단
```

## 참고
- CWE-676, KISA 소프트웨어 개발보안 가이드(2021.12) API 오용 항목
- Thread.stop 폐기 배경과 협력적 중단(interrupt) 패턴
