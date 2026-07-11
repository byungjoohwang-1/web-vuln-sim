# 부적절한 XML 외부개체 참조 (XXE) · CWE-611 · KISA 4.8

## 개념
XXE는 XML 파서가 DOCTYPE 내 외부 엔티티를 확장하도록 허용될 때 발생한다. 공격자는 외부 엔티티로 로컬 파일을 읽거나 내부망에 요청을 보내(SSRF) 정보 유출·서비스 거부를 일으킬 수 있다.

## 취약 원인
- `DocumentBuilderFactory`/`SAXParserFactory` 등을 기본 설정 그대로 사용했다.
- DOCTYPE 선언과 외부 엔티티 처리를 비활성화하지 않았다.
- 외부에서 들어온 XML을 그대로 파싱했다.

## 공격 시나리오
- `<!ENTITY xxe SYSTEM "file:///etc/passwd">` 로 서버 파일을 읽는다.
- `SYSTEM "http://169.254.169.254/..."` 로 클라우드 메타데이터를 조회(SSRF)한다.
- 재귀 엔티티(Billion Laughs)로 메모리를 고갈시켜 DoS를 유발한다.

## 안전한 코딩(핵심 조치)
- `disallow-doctype-decl` 기능을 켜서 DOCTYPE 자체를 거부한다.
- 외부 일반/파라미터 엔티티 로딩과 XInclude를 비활성화한다.
- `XMLConstants.FEATURE_SECURE_PROCESSING` 을 활성화한다.
- 신뢰 불가 XML은 스키마 검증과 함께 처리한다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 파서 설정 | 기본값 | 보안 기능 명시적 설정 |
| DOCTYPE | 허용 | `disallow-doctype-decl=true` |
| 외부 엔티티 | 확장됨 | 로딩 비활성화 |

## CWE·KISA 매핑
- CWE-611: Improper Restriction of XML External Entity Reference
- KISA 소프트웨어 개발보안 가이드(2021) 4장 입력검증 및 표현 — 부적절한 XML 외부개체 참조

## 실행/컴파일 방법
```
javac Vulnerable.java
javac Secure.java

python bugfinder/bugfinder.py examples/1_input-validation/1.08_CWE-611_xxe
```

## 참고
- CWE-611: https://cwe.mitre.org/data/definitions/611.html
- OWASP XXE Prevention Cheat Sheet
