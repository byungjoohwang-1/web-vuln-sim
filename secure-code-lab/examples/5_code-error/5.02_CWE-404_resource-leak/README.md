# 부적절한 자원 해제 (Resource Leak) · CWE-404 · KISA 5.02

## 개념
파일, 소켓, DB 커넥션 같은 시스템 자원을 사용한 뒤 확실히 해제하지 않아 자원이 계속 점유되는 약점이다. 특히 예외가 발생하는 경로에서 해제 코드가 건너뛰어지면 누수가 누적된다.

## 취약 원인
- `new FileInputStream(path)`로 스트림을 열고 `close()`를 호출하지 않았다.
- `try-with-resources`나 `finally` 블록이 없어 예외 발생 시 스트림이 닫히지 않는다.
- 반환/예외 등 어떤 종료 경로에서도 해제를 보장하지 못한다.

## 영향
- 파일 디스크립터가 누적되어 결국 "Too many open files"로 새 자원 확보가 실패한다.
- DB 커넥션 누수는 커넥션 풀 고갈로 이어져 전체 서비스가 멈출 수 있다.
- 잠긴 파일 핸들이 남아 다른 프로세스의 접근을 방해할 수 있다.

## 안전한 코딩
- `try (FileInputStream fis = new FileInputStream(path)) { ... }` 형태의 try-with-resources를 사용해 블록 종료 시 자동으로 `close()`가 호출되게 한다.
- 구형 코드라면 `finally` 블록에서 반드시 해제하고, 해제 중 예외도 처리한다.
- 여러 자원은 하나의 try-with-resources에 함께 선언해 역순으로 안전하게 닫는다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 해제 방식 | 없음 | try-with-resources |
| 예외 발생 시 | 핸들 누수 | 자동 `close()` 보장 |
| 코드 구조 | 열기만 함 | `try ( ... )` 블록 |

## CWE·KISA 매핑
- CWE-404: Improper Resource Shutdown or Release
- KISA 소프트웨어 개발보안 가이드(2021) 5장 코드오류 — 부적절한 자원 해제 (5.02)

## 실행/컴파일 방법
```
javac Vulnerable.java && java Vulnerable   # 스트림 미해제(누수)
javac Secure.java && java Secure           # try-with-resources 자동 해제

# 프로젝트 루트에서 탐지 검증
python bugfinder/bugfinder.py examples/5_code-error/5.02_CWE-404_resource-leak
```

## 참고
- CWE-404: https://cwe.mitre.org/data/definitions/404.html
- Java Language Spec: try-with-resources (JLS 14.20.3)
