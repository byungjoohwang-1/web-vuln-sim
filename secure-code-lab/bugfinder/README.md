# Bug Finder — 동작 원리

`bugfinder.py` 는 표준 라이브러리만 사용하는 **경량 패턴 기반 정적분석기**다.
KISA 개발보안 가이드의 49개 구현단계 보안약점을 정규식 규칙으로 탐지한다.

## 규칙 구조 (`rules.json`)

```jsonc
{
  "num": "1.01", "cwe": "CWE-89", "cat": "입력검증 및 표현",
  "catSlug": "1_input-validation", "slug": "sql-injection",
  "lang": "java", "ko": "SQL 삽입", "sev": "High",
  "danger":    "execute(Query|Update)?\\s*\\(\\s*[^)]*\"\\s*\\+ ...",  // 위험 싱크
  "sanitizer": "PreparedStatement|setString\\s*\\("                    // 완화 지표
}
```

## 판정 로직

한 파일에 대해, 언어가 일치하는 각 규칙을 적용한다.

```
if (danger 정규식이 매칭됨) and (sanitizer 가 없거나(빈 값) or 파일 어디에도 sanitizer 가 매칭되지 않음):
        → 약점으로 보고 (CWE, 심각도, 라인, 스니펫)
else:
        → 억제 (안전한 코드로 간주)
```

- **danger** = 취약해질 수 있는 위험한 호출/구문 (예: 문자열 연결 SQL, `strcpy`, `new Random()`).
- **sanitizer** = 그 위험을 무력화하는 안전 조치 (예: `PreparedStatement`, `snprintf`, `SecureRandom`).
- sanitizer 가 빈 문자열인 규칙(디버그 코드·주석 내 비밀정보)은 **danger 매칭 시 무조건 보고**한다.

이 "위험 싱크 + 완화 지표" 방식은 웹 사이트의 `codefix-grader.js` 채점기와 동일한 철학이며,
단순 grep 보다 오탐이 훨씬 적다.

## 언어 지원
- `.java` → java 규칙 44종
- `.c` `.h` `.cpp` → c 규칙 5종
- (파일 확장자로 언어를 판별하며, 매칭되는 언어의 규칙만 적용)

## 자가검증 (`--selftest`)
`examples/` 를 순회하며 폴더명의 `CWE-xxx` 로 규칙을 찾아:
- **Vulnerable*** 파일은 그 CWE로 **탐지되어야** 한다 (미탐=FN 이면 실패).
- **Secure*** 파일은 그 CWE로 **탐지되지 않아야** 한다 (오탐=FP 이면 실패).

현재 기준: **98건 검사 · 통과 98 · FN 0 · FP 0**.

## 한계 (반드시 인지)
- 정규식 기반이라 **데이터 흐름(taint)·경로 민감도**를 추적하지 못한다.
- "검사 누락"류 약점(인증·권한·시도 제한 부재)은 **위험 구문 존재 + 완화 지표 부재**로 근사 탐지한다 → 다른 안전 코드에서 교차 오탐이 날 수 있다.
- 교육 예제에 맞춰 규칙을 조정했으므로, **임의의 실무 코드에는 오탐/미탐**이 발생한다.
- 실무에서는 상용/오픈소스 SAST(Semgrep, CodeQL, SonarQube, Fortify 등)와 병행하라.

## 규칙 추가/수정
`rules.json` 의 `rules` 배열에 항목을 추가하면 자동으로 반영된다.
정규식은 Python `re` 문법이며, JSON 이므로 백슬래시를 `\\` 로 이스케이프한다.
추가 후 `python bugfinder.py --selftest` 로 회귀를 확인한다.
