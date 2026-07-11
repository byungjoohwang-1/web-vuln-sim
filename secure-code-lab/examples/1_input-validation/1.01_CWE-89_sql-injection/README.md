# SQL 삽입 (SQL Injection) · CWE-89 · KISA 4.1

## 개념
SQL 삽입은 애플리케이션이 외부 입력값을 검증·분리 없이 SQL 질의문에 끼워 넣을 때, 공격자가 질의문의 구조 자체를 바꾸어 데이터베이스를 조작하는 약점이다. 입력값이 '데이터'가 아니라 '실행 코드'로 해석되는 것이 문제의 본질이다.

## 취약 원인
- 사용자 입력을 문자열 연결(`+`)로 SQL 문장에 직접 이어 붙였다.
- `Statement.executeQuery("... '" + id + "'")` 처럼 동적으로 조립된 질의를 그대로 실행했다.
- 입력에 포함된 따옴표, 주석 기호, 논리 연산자가 그대로 SQL 문법으로 전달된다.

## 공격 시나리오
- 로그인 폼에 `id = ' OR '1'='1` 을 입력하면 WHERE 절이 항상 참이 되어 인증이 우회된다.
- `; DROP TABLE members --` 형태로 다중 구문을 넣어 테이블을 삭제한다.
- `UNION SELECT card_no FROM cards` 로 다른 테이블의 민감정보를 조회한다.

## 안전한 코딩(핵심 조치)
- `PreparedStatement` 와 파라미터 바인딩(`setString`, `setInt`)을 사용해 질의 골격과 값을 분리한다.
- 쿼리 문자열에는 `?` 자리표시자만 두고, 값은 바인딩 API로만 전달한다.
- 저장 프로시저를 쓰더라도 내부에서 동적 SQL을 조립하지 않는다.
- 입력값에 대한 형식 검증(화이트리스트)을 병행한다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 질의 조립 | 문자열 연결 `"... '" + id` | 고정 골격 `"... = ?"` |
| 실행 API | `Statement.executeQuery(연결문자열)` | `PreparedStatement.executeQuery()` |
| 입력 취급 | SQL 코드로 해석 | 순수 데이터로 바인딩 |

## CWE·KISA 매핑
- CWE-89: Improper Neutralization of Special Elements used in an SQL Command
- KISA 소프트웨어 개발보안 가이드(2021) 4장 입력검증 및 표현 — SQL 삽입

## 실행/컴파일 방법
```
javac Vulnerable.java   # 취약 코드 컴파일 (실행에는 H2 등 JDBC 드라이버 필요)
javac Secure.java       # 안전 코드 컴파일

# 프로젝트 루트에서 탐지 검증
python bugfinder/bugfinder.py examples/1_input-validation/1.01_CWE-89_sql-injection
```

## 참고
- CWE-89: https://cwe.mitre.org/data/definitions/89.html
- OWASP SQL Injection Prevention Cheat Sheet
