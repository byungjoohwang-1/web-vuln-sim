# 코드 삽입 (Code Injection) · CWE-94 · KISA 4.2

## 개념
코드 삽입은 외부 입력이 프로그램의 실행 코드로 해석·평가될 때 발생한다. 스크립트 엔진의 `eval`, 동적 클래스 로딩, 템플릿 엔진 등에 검증되지 않은 입력이 전달되면 공격자가 서버에서 임의 코드를 실행할 수 있다.

## 취약 원인
- 외부 입력을 `ScriptEngine.eval()` 같은 코드 평가 함수에 직접 전달했다.
- 입력을 '데이터'가 아니라 '실행할 코드'로 다뤘다.
- 실행 가능한 연산의 범위를 제한하지 않았다.

## 공격 시나리오
- 계산기 기능의 수식 입력란에 `java.lang.Runtime.getRuntime().exec('rm -rf /')` 를 넣어 명령을 실행한다.
- 스크립트 엔진을 통해 파일 시스템·네트워크·클래스로더에 접근한다.
- 표현식 언어(EL/OGNL) 삽입으로 서버 내부 객체를 조작한다.

## 안전한 코딩(핵심 조치)
- 외부 입력을 코드로 평가하는 기능(`eval`, 스크립트 엔진)을 제거한다.
- 꼭 필요하면 허용된 연산만 화이트리스트(`ALLOWLIST`)로 정의하고 입력은 선택 키로만 쓴다.
- `switch` 등 고정 분기로 정의된 동작만 수행한다.
- 부득이하게 스크립트를 써야 하면 샌드박스/권한 최소화를 적용한다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 실행 방식 | `engine.eval(입력)` | `ALLOWLIST` + `switch` 분기 |
| 입력 역할 | 실행 코드 | 허용목록 선택 키 |
| 결과 | 임의 코드 실행 | 정의된 연산만 수행 |

## CWE·KISA 매핑
- CWE-94: Improper Control of Generation of Code ('Code Injection')
- KISA 소프트웨어 개발보안 가이드(2021) 4장 입력검증 및 표현 — 코드 삽입

## 실행/컴파일 방법
```
javac Vulnerable.java
javac Secure.java

python bugfinder/bugfinder.py examples/1_input-validation/1.02_CWE-94_code-injection
```

## 참고
- CWE-94: https://cwe.mitre.org/data/definitions/94.html
- OWASP Code Injection
