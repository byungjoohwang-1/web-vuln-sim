# Null Pointer 역참조 (Null Pointer Dereference) · CWE-476 · KISA 5.01

## 개념
프로그램이 값이 `null`(또는 C의 `NULL`)일 수 있는 참조를 확인 없이 역참조할 때 발생하는 약점이다. 자바에서는 `NullPointerException`이 던져져 요청이 비정상 종료되고, 서버는 자원을 정리하지 못한 채 예외 흐름으로 빠질 수 있다.

## 취약 원인
- `request.getParameter("keyword")`는 해당 파라미터가 없으면 `null`을 반환한다.
- 반환값을 `null` 검사 없이 곧바로 `.trim().toLowerCase()`로 역참조했다.
- 외부 입력이 존재한다는 암묵적 가정을 코드가 검증하지 않는다.

## 영향
- 필수 파라미터 누락이라는 정상적으로 발생 가능한 입력만으로 서비스가 예외로 중단된다.
- 예외가 사용자에게 그대로 노출되면 스택트레이스로 내부 구조가 유출될 수 있다.
- 반복 유발 시 특정 엔드포인트에 대한 서비스 거부(DoS)로 악용될 수 있다.

## 안전한 코딩
- 역참조 전에 `if (raw == null)` 또는 `raw != null`로 null 여부를 확인하고 안전한 기본값으로 대체한다.
- 반드시 값이 있어야 하는 필수 입력은 `Objects.requireNonNull(value, "메시지")`로 계약을 명시해 조기에 실패시킨다.
- `Optional`을 활용해 null 가능성을 타입 수준에서 드러낼 수 있다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| null 검사 | 없음 | `raw == null` 확인 후 기본값 |
| 필수값 처리 | 가정에만 의존 | `Objects.requireNonNull` |
| 파라미터 누락 시 | `NullPointerException` | 빈 문자열 등 안전 반환 |

## CWE·KISA 매핑
- CWE-476: NULL Pointer Dereference
- KISA 소프트웨어 개발보안 가이드(2021) 5장 코드오류 — Null Pointer 역참조 (5.01)

## 실행/컴파일 방법
```
javac Vulnerable.java && java Vulnerable   # keyword 누락으로 NPE 재현
javac Secure.java && java Secure           # 예외 없이 안전 처리

# 프로젝트 루트에서 탐지 검증
python bugfinder/bugfinder.py examples/5_code-error/5.01_CWE-476_null-pointer-dereference
```

## 참고
- CWE-476: https://cwe.mitre.org/data/definitions/476.html
- Oracle Java: `java.util.Objects.requireNonNull`, `java.util.Optional`
