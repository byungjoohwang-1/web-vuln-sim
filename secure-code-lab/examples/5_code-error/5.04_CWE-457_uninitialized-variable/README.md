# 초기화되지 않은 변수 사용 (Use of Uninitialized Variable) · CWE-457 · KISA 5.04

## 개념
값을 대입하기 전의 변수를 읽어서 사용하는 약점이다. C의 지역 변수는 자동으로 0이 되지 않고 스택에 남아 있던 쓰레기 값을 가지므로, 초기화 없이 사용하면 실행할 때마다 결과가 달라진다.

## 취약 원인
- `int total;`처럼 초기값 없이 선언한 뒤 곧바로 누산(`total += ...`)에 사용했다.
- 시작값이 정의되지 않아 합계가 예측 불가능해진다.
- 컴파일러 최적화나 스택 배치에 따라 값이 매번 달라질 수 있다.

## 영향
- 계산 결과가 비결정적이라 재현 불가능한 버그가 발생한다.
- 이 값으로 버퍼 크기나 인덱스를 정하면 오버플로우/범위 초과로 이어질 수 있다.
- 초기화되지 않은 값이 조건 분기를 좌우하면 보안 검사 우회로도 악용될 수 있다.

## 안전한 코딩
- 선언과 동시에 초기화한다: `int total = 0;`.
- 배열/구조체는 `= { 0 }` 또는 `memset(buf, 0, sizeof(buf))`로 0 채움한다.
- 동적 할당 시 0 초기화가 필요하면 `calloc`을 사용한다.
- 컴파일 시 `-Wall -Wuninitialized`(및 `-O2`)로 경고를 활성화해 조기에 잡는다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.c) | 안전 (Secure.c) |
|------|---------------------|------------------|
| 선언 | `int total;` (bare) | `int total = 0;` |
| 시작값 | 스택 쓰레기 값 | 명시적 0 |
| 배열 초기화 | 해당 없음 | `memset(..., 0, ...)` |

## CWE·KISA 매핑
- CWE-457: Use of Uninitialized Variable
- KISA 소프트웨어 개발보안 가이드(2021) 5장 코드오류 — 초기화되지 않은 변수 사용 (5.04)

## 실행/컴파일 방법
```
gcc -Wall -Wuninitialized -O2 Vulnerable.c -o vuln   # 경고와 함께 비결정적 결과
gcc -Wall -Wuninitialized -O2 Secure.c -o safe

./vuln     # 실행마다 합계가 달라질 수 있음
./safe     # 항상 sum=600

# 프로젝트 루트에서 탐지 검증
python bugfinder/bugfinder.py examples/5_code-error/5.04_CWE-457_uninitialized-variable
```

## 참고
- CWE-457: https://cwe.mitre.org/data/definitions/457.html
- GCC 경고: `-Wuninitialized`, `-Wmaybe-uninitialized`
