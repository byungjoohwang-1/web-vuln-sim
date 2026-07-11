## 메모리 버퍼 오버플로우 (Buffer Overflow) — CWE-120 / KISA 1.16

## 개념
버퍼 오버플로우는 고정 크기 버퍼에 그 크기를 초과하는 데이터를 복사할 때 발생한다. 초과분이 인접 메모리(다른 지역변수, 저장된 프레임 포인터/반환주소)를 덮어써 프로그램이 오작동하거나, 공격자가 반환주소를 조작해 임의 코드를 실행할 수 있다.

## 취약 원인
- `strcpy`, `strcat`, `sprintf`, `gets`처럼 대상 버퍼 크기를 받지 않는 함수를 사용한다.
- 외부 입력의 길이를 검사하지 않는다.
- 남은 버퍼 공간을 계산하지 않고 연결/포맷팅한다.

## 공격 시나리오
1. `greet(argv[1])`가 32바이트 스택 버퍼에 인자를 `strcat`한다.
2. 공격자가 100바이트 문자열을 인자로 넘긴다.
3. 복사가 버퍼 경계를 넘어 저장된 반환주소를 덮어쓴다.
4. 반환 시 공격자가 지정한 주소로 점프해 셸코드가 실행될 수 있다.

## 안전한 코딩
- 크기를 명시하는 함수(`strncpy`, `strncat`, `snprintf`)를 쓰고, 항상 NUL 종료를 보장한다.
- 표준 입력은 `gets` 대신 `fgets(buf, sizeof(buf), stdin)`으로 길이를 제한한다.
- 남은 공간(`sizeof - strlen - 1`)을 계산해 연결한다.
- 컴파일러 보호(`-D_FORTIFY_SOURCE=2`, 스택 카나리)를 병행한다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable.c) | 안전(Secure.c) |
|------|--------------------|----------------|
| 복사 | `strcpy`/`strcat`/`sprintf` | `strncpy`/`strncat`/`snprintf` |
| 입력 | 무제한 | `fgets`로 길이 제한 |
| NUL 종료 | 보장 안 됨 | 명시적으로 보장 |

## CWE·KISA 매핑
- CWE-120: Buffer Copy without Checking Size of Input ('Classic Buffer Overflow')
- KISA 소프트웨어 개발보안 가이드(2021) 입력검증 및 표현 — 1.16 메모리 버퍼 오버플로우

## 실행/컴파일 방법
```
gcc -Wall Vulnerable.c -o vuln && ./vuln $(python -c "print('A'*100)")
gcc -Wall Secure.c    -o safe && echo "someone" | ./safe
```
버그 파인더 검증:
```
python bugfinder/bugfinder.py examples/1_input-validation/1.16_CWE-120_buffer-overflow
```

## 참고
- CWE-120 (MITRE)
- CERT C STR31-C, STR07-C
- 소프트웨어 개발보안 가이드(2021) 1.16
