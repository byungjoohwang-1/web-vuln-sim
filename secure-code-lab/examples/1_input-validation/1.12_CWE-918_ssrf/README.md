## 서버사이드 요청 위조 (SSRF) — CWE-918 / KISA 1.12

## 개념
SSRF는 공격자가 서버가 보내는 요청의 목적지를 조종할 수 있을 때 발생한다. 서버는 방화벽 안쪽에 있으므로, 검증되지 않은 URL을 그대로 요청하면 공격자는 서버를 프록시 삼아 내부망 자원(클라우드 메타데이터, 내부 관리 API, 로컬 서비스)에 접근하게 된다.

## 취약 원인
- 사용자 입력 URL을 검증 없이 `new URL(...)`에 넣고 `openConnection()`으로 요청한다.
- 목적지 스킴/호스트/IP 대역에 대한 제한(화이트리스트)이 없다.
- 리다이렉트와 DNS 재바인딩을 고려하지 않는다.

## 공격 시나리오
1. 이미지 미리보기 기능에 `target` 파라미터로 임의 URL을 받는다.
2. 공격자가 `http://169.254.169.254/latest/meta-data/iam/security-credentials/`를 지정한다.
3. 서버가 클라우드 메타데이터 엔드포인트에 접근해 임시 자격증명을 읽어 응답에 담아 유출한다.
4. `http://127.0.0.1:8080/admin` 등 내부 서비스 스캔·호출에도 악용된다.

## 안전한 코딩
- 목적지를 허용 호스트 화이트리스트로 제한한다.
- 스킴을 `https`로 강제하고, 사설 IP 대역(10/8, 172.16/12, 192.168/16, 127/8, 169.254/16)을 차단한다.
- URL을 파싱해 호스트를 검증하고, 리다이렉트 자동 추적을 끄거나 재검증한다.
- 별도 아웃바운드 프록시/egress 정책으로 네트워크 계층에서도 통제한다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable.java) | 안전(Secure.java) |
|------|----------------------|-------------------|
| 목적지 검증 | 없음 | ALLOWLIST + isAllowedHost |
| 스킴 | 무제한 | https만 허용 |
| 내부망 접근 | 가능 | 거부(SecurityException) |

## CWE·KISA 매핑
- CWE-918: Server-Side Request Forgery (SSRF)
- KISA 소프트웨어 개발보안 가이드(2021) 입력검증 및 표현 — 1.12 서버사이드 요청 위조

## 실행/컴파일 방법
서블릿 API가 필요하다.
```
javac -cp servlet-api.jar Vulnerable.java Secure.java
java Secure
```
버그 파인더 검증:
```
python bugfinder/bugfinder.py examples/1_input-validation/1.12_CWE-918_ssrf
```

## 참고
- CWE-918 (MITRE)
- OWASP SSRF Prevention Cheat Sheet
- 소프트웨어 개발보안 가이드(2021) 1.12
