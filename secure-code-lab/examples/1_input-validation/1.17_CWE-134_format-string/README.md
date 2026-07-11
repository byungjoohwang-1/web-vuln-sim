## 포맷 스트링 삽입 (Format String) — CWE-134 / KISA 1.17

## 개념
포맷 스트링 취약점은 외부 입력을 `printf`, `fprintf`, `syslog` 같은 함수의 포맷 문자열 인자로 직접 사용할 때 발생한다. 입력에 `%x`, `%s`, `%n` 같은 변환지정자가 포함되면 함수는 실재하지 않는 인자를 스택에서 읽어 정보를 유출하거나(`%x`, `%s`), `%n`으로 임의 메모리에 값을 써서 코드 실행까지 가능하다.

## 취약 원인
- `printf(userInput)`처럼 사용자 입력을 포맷 문자열 자리에 넣는다.
- 포맷 지정자를 고정 상수로 두지 않는다.
- 로깅/오류 출력 경로에서 입력을 그대로 포맷으로 흘려보낸다.

## 공격 시나리오
1. 로그 함수가 `printf(userInput)`로 사용자 메시지를 출력한다.
2. 공격자가 `%x %x %x %x`를 입력하면 스택 값(주소, 데이터)이 유출된다.
3. `%s`로 임의 포인터를 문자열로 역참조해 크래시나 정보 유출을 유발한다.
4. `%n`으로 특정 주소에 값을 써 반환주소/함수 포인터를 조작하고 코드 실행을 시도한다.

## 안전한 코딩
- 포맷 문자열은 항상 개발자가 고정한 상수로 지정한다: `printf("%s", userInput)`.
- 사용자 입력은 포맷이 아니라 대응 인자로만 전달한다.
- 컴파일러 경고(`-Wformat -Wformat-security`)를 켜서 위험 호출을 잡는다.
- 폭 제한(`%.100s`)으로 과도한 출력을 막는다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable.c) | 안전(Secure.c) |
|------|--------------------|----------------|
| 포맷 인자 | 사용자 입력 자체 | 고정 상수 `"%s"` |
| `%n` 처리 | 임의 메모리 쓰기 | 평범한 문자로 출력 |
| 정보 유출 | 스택 노출 | 없음 |

## CWE·KISA 매핑
- CWE-134: Use of Externally-Controlled Format String
- KISA 소프트웨어 개발보안 가이드(2021) 입력검증 및 표현 — 1.17 포맷 스트링 삽입

## 실행/컴파일 방법
```
gcc -Wall -Wformat -Wformat-security Vulnerable.c -o vuln && ./vuln "%x %x %x"
gcc -Wall -Wformat -Wformat-security Secure.c    -o safe && ./safe "%x %x %x"
```
취약 버전은 스택 값을 출력하고, 안전 버전은 `%x %x %x`를 문자 그대로 출력한다.
버그 파인더 검증:
```
python bugfinder/bugfinder.py examples/1_input-validation/1.17_CWE-134_format-string
```

## 참고
- CWE-134 (MITRE)
- CERT C FIO30-C
- 소프트웨어 개발보안 가이드(2021) 1.17
