## LDAP 삽입 (LDAP Injection) — CWE-90 / KISA 1.10

## 개념
LDAP 삽입은 애플리케이션이 사용자 입력을 LDAP 검색 필터나 DN(Distinguished Name)에 검증 없이 결합할 때 발생한다. 공격자는 `*`, `(`, `)`, `\`, `|`, `&` 같은 LDAP 메타문자를 주입해 필터의 논리 구조를 바꾸고, 인증 우회나 디렉터리 정보 무단 열람을 시도한다.

## 취약 원인
- 사용자 입력을 `"(uid=" + userInput + ")"` 형태로 필터 문자열에 직접 이어붙인다.
- LDAP 특수문자를 이스케이프하지 않는다.
- 결합된 필터를 그대로 `DirContext.search()`에 전달한다.

## 공격 시나리오
1. 로그인 폼의 아이디 입력란에 `*)(uid=*))(|(uid=*` 를 입력한다.
2. 필터가 `(uid=*)(uid=*))(|(uid=*)` 로 변형되어 모든 사용자와 매칭된다.
3. 비밀번호 검증이 필터 결과에 의존한다면 임의 계정으로 인증이 우회된다.
4. `admin)(userPassword=*` 같은 값으로 특정 속성 존재 여부를 탐색(블라인드)할 수도 있다.

## 안전한 코딩
- 사용자 입력을 필터에 넣기 전 RFC 4515 규칙으로 이스케이프한다(`* → \2a`, `( → \28`, `) → \29`, `\ → \5c`, `NUL → \00`).
- OWASP ESAPI `encodeForLDAP`/`encodeForDN` 또는 동등한 escape 유틸리티를 사용한다.
- 가능하면 필터 자리표시자(`{0}`)와 arguments 배열을 사용해 결합을 피한다.
- 입력값을 화이트리스트(허용 문자 집합)로 추가 검증한다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable.java) | 안전(Secure.java) |
|------|----------------------|-------------------|
| 필터 구성 | 입력을 문자열로 직접 결합 | 이스케이프 후 자리표시자 인자로 전달 |
| 메타문자 | 그대로 필터 논리에 반영 | `\2a` 등으로 무력화 |
| 결과 | 인증 우회·정보 유출 | 입력을 데이터로만 취급 |

## CWE·KISA 매핑
- CWE-90: Improper Neutralization of Special Elements used in an LDAP Query
- KISA 소프트웨어 개발보안 가이드(2021) 입력검증 및 표현 — 1.10 LDAP 삽입

## 실행/컴파일 방법
JNDI(`javax.naming`)는 JDK 표준 라이브러리라 별도 의존성 없이 컴파일된다.
```
javac Vulnerable.java Secure.java
java Secure   # escapeFilter 결과 확인
```
버그 파인더 검증:
```
python bugfinder/bugfinder.py examples/1_input-validation/1.10_CWE-90_ldap-injection
```

## 참고
- CWE-90 (MITRE)
- OWASP LDAP Injection Prevention Cheat Sheet, RFC 4515
- 소프트웨어 개발보안 가이드(2021) 1.10
