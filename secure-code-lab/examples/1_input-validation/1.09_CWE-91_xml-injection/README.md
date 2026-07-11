# XML 삽입 (XML Injection) · CWE-91 · KISA 4.9

## 개념
XML 삽입은 외부 입력이 검증·이스케이프 없이 XML 문서에 삽입되어, 공격자가 태그·요소·속성을 주입해 문서 구조나 의미를 바꾸는 약점이다. 데이터 위조, 권한 상승, 후속 파서의 오작동으로 이어질 수 있다.

## 취약 원인
- 입력을 문자열 연결(`+`)로 XML 문서에 직접 삽입했다.
- `<`, `>`, `&`, 따옴표 같은 XML 특수문자를 이스케이프하지 않았다.
- 값을 '데이터'가 아니라 '마크업'으로 취급했다.

## 공격 시나리오
- 이름 필드에 `guest</role><role>admin` 을 넣어 권한 요소를 위조한다.
- `<![CDATA[...]]>` 나 새 태그를 주입해 문서 구조를 변형한다.
- 후속 XPath/XSLT 처리에 영향을 주는 요소를 삽입한다.

## 안전한 코딩(핵심 조치)
- 값을 XML에 넣기 전 특수문자를 엔티티로 이스케이프한다(`escapeXml`, `StringEscapeUtils.escapeXml`).
- 문자열 조립 대신 DOM API(`setTextContent`, `createTextNode`)로 값을 넣는다.
- 입력 형식을 스키마/화이트리스트로 검증한다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 삽입 방식 | `"<name>" + input` | `escapeXml(input)` 후 삽입 |
| 특수문자 | 그대로 마크업 | 엔티티로 변환 |
| 결과 | 구조 위조 가능 | 텍스트 데이터로 고정 |

## CWE·KISA 매핑
- CWE-91: XML Injection (aka Blind XPath Injection)
- KISA 소프트웨어 개발보안 가이드(2021) 4장 입력검증 및 표현 — XML 삽입

## 실행/컴파일 방법
```
javac Vulnerable.java
javac Secure.java

python bugfinder/bugfinder.py examples/1_input-validation/1.09_CWE-91_xml-injection
```

## 참고
- CWE-91: https://cwe.mitre.org/data/definitions/91.html
- OWASP XML Injection
