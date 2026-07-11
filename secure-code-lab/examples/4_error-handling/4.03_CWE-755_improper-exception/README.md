# 부적절한 예외 처리 · CWE-755 · KISA 에러처리

## 개념
CWE-755는 예외나 오류 조건을 부적절하게 처리하는 약점이다. 대표적으로 성격이 다른 여러 예외를 `catch (Exception)`이나 `catch (Throwable)`처럼 지나치게 광범위하게 한꺼번에 잡는 경우가 있다. 이렇게 하면 각 오류에 맞는 대응이 불가능하고, 프로그래밍 버그로 인한 런타임 예외까지 함께 삼켜져 문제가 감춰진다.

## 취약 원인
- `catch (Exception e)`로 IO 오류, 형식 오류, 인덱스 오류, 널 참조 등을 구분 없이 처리했다.
- `NullPointerException` 같은 프로그래밍 버그(RuntimeException)까지 정상 흐름처럼 삼켜진다.
- 원인별 복구 전략을 세울 수 없고, 항상 같은 방식(예: 0 반환)으로 얼버무린다.

## 공격 시나리오(영향)
- 진짜 결함(널 참조·논리 오류)이 광범위 catch에 묻혀 발견이 늦어진다.
- 잘못된 기본값으로 계속 동작해 데이터 무결성이 훼손되거나 보안 검증이 우회된다.
- 서로 다른 실패를 동일하게 취급하여 장애 원인 분석과 복구가 어려워진다.

## 안전한 코딩
- 발생 가능한 예외를 유형별로 구체적으로 잡는다(`IOException`, `NumberFormatException` 등).
- 광범위한 `catch (Exception)` / `catch (Throwable)`를 지양한다.
- 예상하지 못한 예외는 잡지 않고 전파시켜, 버그가 드러나도록 한다.
- 각 예외에 맞는 로깅·복구·기본값 전략을 명시한다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| catch 범위 | `catch (Exception e)` 하나 | `IOException`, `NumberFormatException` 개별 |
| 버그 처리 | RuntimeException까지 삼킴 | 예상 밖 예외는 전파 |
| 원인 구분 | 불가능 | 유형별 로깅·대응 |
| 복구 전략 | 획일적(0 반환) | 상황별 기본값·전파 |

## CWE·KISA 매핑
- CWE-755: Improper Handling of Exceptional Conditions
- KISA 소프트웨어 개발보안 가이드(2021) — 에러처리: 부적절한 예외 처리

## 실행/컴파일 방법
```
javac Vulnerable.java
javac Secure.java

# 프로젝트 루트에서 탐지 검증
python bugfinder/bugfinder.py examples/4_error-handling/4.03_CWE-755_improper-exception
```

## 참고
- CWE-755: https://cwe.mitre.org/data/definitions/755.html
