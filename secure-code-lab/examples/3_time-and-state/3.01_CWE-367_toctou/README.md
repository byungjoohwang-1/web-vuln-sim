# 경쟁조건: 검사시점과 사용시점(TOCTOU) · CWE-367 · KISA 시간 및 상태

## 개념
TOCTOU(Time Of Check to Time Of Use)는 어떤 자원의 상태를 "검사"한 시점과 그 검사 결과를 믿고 자원을 "사용"하는 시점이 분리되어 있을 때 발생하는 경쟁조건 약점이다. 두 시점 사이의 짧은 시간 동안 다른 프로세스나 스레드가 자원의 상태를 바꾸면, 이미 검증했다고 믿은 전제가 깨진다.

## 취약 원인
- `file.exists()`로 파일 존재 여부를 먼저 검사하고, 그 결과를 신뢰해 뒤이어 파일을 생성·열기한다.
- 검사와 사용이 별개의 연산으로 나뉘어 있어 그 사이에 상태가 바뀔 수 있다(경쟁 윈도우 존재).
- 파일 시스템 접근이 원자적으로 보호되지 않는다.

## 공격 시나리오(영향)
- 잠금 파일 기반 상호배제가 무력화되어 두 프로세스가 동시에 임계 구역에 진입한다.
- 공격자가 검사 직후 같은 경로에 심볼릭 링크나 파일을 심어, 프로그램이 의도치 않은 대상에 쓰기(권한 상승·파일 덮어쓰기)를 수행하게 만든다.
- 잠금이 깨져 이중 처리, state 손상, 데이터 경합이 발생한다.

## 안전한 코딩
- 검사와 사용을 하나의 원자적 연산으로 합친다.
- `Files.newOutputStream(path, StandardOpenOption.CREATE_NEW)` 또는 `Files.createFile(...)`처럼 "없을 때만 생성"하는 원자적 API를 사용하고, 이미 존재하면 예외로 처리한다.
- 공유 자원 접근이 필요하면 `synchronized`나 `FileLock`으로 임계 구역을 보호한다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 존재 확인 | `file.exists()`로 사전 검사 | 사전 검사 없이 원자적 생성 시도 |
| 생성 방식 | 검사 후 별도로 `FileWriter` 생성 | `CREATE_NEW`로 없을 때만 원자 생성 |
| 경쟁 윈도우 | 검사~사용 사이 존재 | 없음 |
| 충돌 처리 | 감지 못함(덮어쓰기 위험) | `FileAlreadyExistsException`으로 감지 |

## CWE·KISA 매핑
- CWE-367: Time-of-check Time-of-use (TOCTOU) Race Condition
- KISA 소프트웨어 개발보안 가이드(2021) — 시간 및 상태: 경쟁조건(검사시점과 사용시점)

## 실행/컴파일 방법
```
javac Vulnerable.java
javac Secure.java

# 프로젝트 루트에서 탐지 검증
python bugfinder/bugfinder.py examples/3_time-and-state/3.01_CWE-367_toctou
```

## 참고
- CWE-367: https://cwe.mitre.org/data/definitions/367.html
- OWASP: Time of Check to Time of Use (TOCTOU) Race Conditions
