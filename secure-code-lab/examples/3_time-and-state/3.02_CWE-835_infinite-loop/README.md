# 종료되지 않는 반복문 또는 재귀 함수 · CWE-835 · KISA 시간 및 상태

## 개념
반복문이나 재귀는 반드시 도달 가능한 종료 조건을 가져야 한다. 종료 조건이 없거나 어떤 경로로도 조건이 참이 되지 않으면, 실행이 끝나지 않아 CPU를 점유한 채 프로그램이 멈춘 것처럼 동작한다. 이를 무한 루프(또는 무한 재귀)라고 한다.

## 취약 원인
- `while (true)`(또는 `for (;;)`)를 사용하면서 루프를 빠져나갈 경로를 두지 않았다.
- 큐가 비었거나 더 이상 처리할 작업이 없어도 루프가 계속 돈다(바쁜 대기).
- 반복 횟수 상한이나 시간 제한 같은 안전장치가 없다.

## 공격 시나리오(영향)
- 워커 스레드가 무한 회전하며 CPU를 100% 점유해 서비스가 응답 불능(DoS)에 빠진다.
- 공격자가 특정 입력으로 종료 조건이 성립하지 않는 상태를 유발하면 자원 고갈을 일으킬 수 있다.
- 무한 재귀의 경우 `StackOverflowError`로 프로세스가 비정상 종료된다.

## 안전한 코딩
- 모든 반복문에 도달 가능한 종료 조건을 둔다. 처리할 것이 없으면 `break`로 벗어난다.
- 최대 반복 횟수(`counter < maxIter`) 또는 시간 상한을 두어, 예외적 상황에서도 무한 회전을 막는다.
- 재귀는 종료(base case)를 명확히 하고 재귀 깊이를 제한한다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 루프 조건 | `while (true)` | `while (counter < maxIter)` |
| 탈출 경로 | 없음 | 큐 소진 시 `break` |
| 반복 상한 | 없음 | `maxIter`로 강제 |
| 종료 보장 | 없음(무한 회전) | 반드시 종료 |

## CWE·KISA 매핑
- CWE-835: Loop with Unreachable Exit Condition ('Infinite Loop')
- KISA 소프트웨어 개발보안 가이드(2021) — 시간 및 상태: 종료되지 않는 반복문 또는 재귀 함수

## 실행/컴파일 방법
```
javac Vulnerable.java   # 주의: main 실행 시 무한 루프에 빠진다(데모용)
javac Secure.java

# 프로젝트 루트에서 탐지 검증
python bugfinder/bugfinder.py examples/3_time-and-state/3.02_CWE-835_infinite-loop
```

## 참고
- CWE-835: https://cwe.mitre.org/data/definitions/835.html
