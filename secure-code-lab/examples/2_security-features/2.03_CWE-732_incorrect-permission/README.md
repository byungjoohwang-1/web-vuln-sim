# 중요자원에 대한 잘못된 권한 설정 (Incorrect Permission Assignment) — CWE-732 / KISA 2.3

## 개념
비밀키, 설정 파일, 로그처럼 민감한 자원에 필요 이상으로 넓은 접근 권한을
부여해, 권한이 없어야 할 사용자나 프로세스가 그 자원을 읽거나 수정할 수 있는
약점이다. 최소 권한 원칙(Principle of Least Privilege)을 위반한 상태다.

## 취약 원인
- `setReadable(true, false)`의 두 번째 인자 `false`는 "소유자만이 아니라 모두"를 뜻한다.
- POSIX 권한을 `0777`/`0666`처럼 넓게 주거나 OTHERS 비트를 켠다.
- "일단 동작하게" 하려고 권한을 완화한 뒤 되돌리지 않는다.

## 공격 시나리오
1. 공유 서버에서 애플리케이션이 `app-secret.conf`를 모두 읽기 가능하게 생성한다.
2. 같은 서버의 다른 계정/프로세스가 파일을 열어 DB 비밀번호를 획득한다.
3. 쓰기까지 허용되면 설정을 변조해 애플리케이션 동작을 조작한다.

## 안전한 코딩
- 민감 파일은 소유자 전용(0700 / `rw-------`)으로 최소 권한을 부여한다.
- Java NIO의 `PosixFilePermission.OWNER_READ/OWNER_WRITE`만 설정한다.
- 비 POSIX 환경에서는 `setReadable(true, true)`로 "소유자에게만" 제한한다.
- 파일 생성 시점부터 안전한 권한을 주고, 나중에 넓히지 않는다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable) | 안전(Secure) |
|------|------------------|--------------|
| 권한 범위 | 전체 사용자(`setReadable(true,false)`) | 소유자 전용(`OWNER_READ`, `rw-------`) |
| 최소 권한 | 위반 | 준수 |
| 타 사용자 접근 | 가능 | 차단 |

## CWE·KISA 매핑
- CWE-732: Incorrect Permission Assignment for Critical Resource
- KISA 소프트웨어 개발보안 가이드(2021.12) 2.3 중요자원에 대한 잘못된 권한 설정

## 실행/컴파일 방법
```bash
javac Vulnerable.java && java Vulnerable
javac Secure.java && java Secure   # POSIX 권한은 Linux/macOS에서 적용됨
```

## 참고
- CWE-732: https://cwe.mitre.org/data/definitions/732.html
- KISA 소프트웨어 개발보안 가이드(2021.12)
