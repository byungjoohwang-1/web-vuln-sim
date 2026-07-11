# 경로 조작 및 자원 삽입 (Path Traversal) · CWE-22 · KISA 4.3

## 개념
경로 조작은 외부 입력이 파일·디렉터리 경로 계산에 검증 없이 사용될 때, 공격자가 `../` 같은 상위 경로 이동 문자열로 의도한 접근 범위를 벗어나는 약점이다. 시스템 파일 열람, 임의 파일 덮어쓰기로 이어질 수 있다.

## 취약 원인
- 기준 디렉터리에 외부 입력 파일명을 문자열 연결(`+`)로 그대로 붙였다.
- 경로 정규화와 기준 경로 소속 검증을 하지 않았다.
- `../`, 절대경로, 심볼릭 링크에 대한 방어가 없다.

## 공격 시나리오
- 다운로드 파라미터에 `name=../../../../etc/passwd` 를 넣어 계정 정보를 읽는다.
- `name=../../config/db.properties` 로 DB 접속정보를 탈취한다.
- 업로드 경로에 `../` 를 넣어 웹 루트에 악성 파일을 배치한다.

## 안전한 코딩(핵심 조치)
- 입력을 붙인 후 `getCanonicalPath()`/`normalize()` 로 실제 경로를 확정한다.
- 확정된 경로가 허용 기준 디렉터리 하위인지 `startsWith` 로 검사한다.
- 파일명은 화이트리스트 문자만 허용하고 경로 구분자를 제거한다.
- 가능하면 사용자 입력 대신 서버가 관리하는 ID→경로 매핑을 사용한다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 경로 계산 | `new File(BASE + name)` | 정규화 후 확정 |
| 검증 | 없음 | `getCanonicalPath` + `startsWith` |
| `../` 처리 | 그대로 통과 | 정규화 후 범위 차단 |

## CWE·KISA 매핑
- CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
- KISA 소프트웨어 개발보안 가이드(2021) 4장 입력검증 및 표현 — 경로 조작 및 자원 삽입

## 실행/컴파일 방법
```
javac Vulnerable.java
javac Secure.java

python bugfinder/bugfinder.py examples/1_input-validation/1.03_CWE-22_path-traversal
```

## 참고
- CWE-22: https://cwe.mitre.org/data/definitions/22.html
- OWASP Path Traversal
