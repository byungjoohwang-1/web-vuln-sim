## 정수형 오버플로우 (Integer Overflow) — CWE-190 / KISA 1.14

## 개념
정수형 오버플로우는 산술 연산 결과가 해당 정수 타입이 표현할 수 있는 범위를 넘어 값이 되돌아오는(wrap-around) 현상이다. 특히 메모리 할당 크기 계산(`count * size`)에서 발생하면 실제 필요한 크기보다 훨씬 작은 버퍼가 할당되고, 이후 데이터를 채우며 힙 경계를 넘어 쓰는 버퍼 오버플로우로 이어진다.

## 취약 원인
- `malloc(count * size)`처럼 두 값을 곱한 결과로 직접 할당한다.
- 곱셈이 `size_t` 범위를 넘는지 사전 검사하지 않는다.
- 할당 성공 여부(NULL)만 확인하고, 실제 크기가 의도와 같은지는 확인하지 않는다.

## 공격 시나리오
1. 파일 헤더나 요청 파라미터에서 원소 개수 `count`를 공격자가 큰 값으로 지정한다.
2. `count * size`가 되돌아와 작은 수(예: 0 또는 수백 바이트)가 된다.
3. `malloc`은 작은 버퍼를 반환하지만 프로그램은 원래 크기만큼 쓴다.
4. 힙 메타데이터가 훼손되어 임의 코드 실행이나 크래시로 이어진다.

## 안전한 코딩
- 곱셈 전에 `if (size != 0 && count > SIZE_MAX / size)`로 오버플로우 가능성을 검사한다.
- 컴파일러 내장 함수 `__builtin_mul_overflow`(또는 `reallocarray`, `calloc`의 곱셈 검사)를 사용한다.
- 사용자 입력 크기값에 상한(최대 원소 수)을 둔다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable.c) | 안전(Secure.c) |
|------|--------------------|----------------|
| 크기 계산 | `malloc(count * size)` 무검사 | 곱셈 전 `count > SIZE_MAX / size` 검사 |
| 오버플로우 | 되돌아온 값으로 할당 | 사전 거부 |
| 결과 | 힙 오버플로우 | 안전 실패(NULL) |

## CWE·KISA 매핑
- CWE-190: Integer Overflow or Wraparound
- KISA 소프트웨어 개발보안 가이드(2021) 입력검증 및 표현 — 1.14 정수형 오버플로우

## 실행/컴파일 방법
```
gcc -O2 -Wall Vulnerable.c -o vuln && ./vuln
gcc -O2 -Wall Secure.c    -o safe && ./safe
```
안전 버전은 "rejected: multiplication would overflow"를 출력한다.
버그 파인더 검증:
```
python bugfinder/bugfinder.py examples/1_input-validation/1.14_CWE-190_integer-overflow
```

## 참고
- CWE-190 (MITRE)
- CERT C INT30-C, MEM07-C
- 소프트웨어 개발보안 가이드(2021) 1.14
