# DNS lookup에 의존한 보안결정 (CWE-350 / KISA 7.01 API 오용)

## 제목
- 약점명: DNS lookup에 의존한 보안결정
- CWE: CWE-350 (Reliance on Reverse DNS Resolution for a Security-Sensitive Action)
- KISA 개발보안 가이드(2021) 항목: 7.01 (API 오용)

## 개념
접속 클라이언트의 IP 를 역방향 DNS(reverse DNS)로 조회해 얻은 "호스트 이름"을
근거로 접근 허용 여부를 결정하는 방식이다. 역방향 DNS 레코드(PTR)는 IP 소유자가
설정할 수 있어, 공격자가 자신의 IP 이름을 신뢰 도메인처럼 위조할 수 있다.

## 취약 원인
- `addr.getHostName()` 으로 얻은 이름이 사내 도메인으로 끝나면 신뢰한다.
- 이름은 공격자 통제하의 DNS 로 위조 가능하므로 보안 결정 근거가 될 수 없다.

## 영향
- 외부 공격자가 내부 사용자로 위장해 접근 통제를 우회한다.
- 인증/인가 판단이 무력화된다.

## 안전한 코딩
- 보안 결정은 위조 가능한 이름이 아니라 실제 접속 IP(`getHostAddress()`)로 한다.
- 사전에 정의한 IP 허용목록(ALLOWLIST)과 정확히 비교한다.
- 이름 기반 신뢰가 필요하면 상호 TLS 인증서 등 위조 불가한 수단을 사용한다.

## 취약 vs 안전 차이
- 취약: `addr.getHostName().endsWith(".internal...")` → 역방향 DNS 이름 신뢰.
- 안전: `ALLOWLIST.contains(addr.getHostAddress())` → 원시 IP 허용목록 비교.

## CWE·KISA 매핑
- CWE-350: Reliance on Reverse DNS Resolution for a Security-Sensitive Action
- KISA 개발보안 가이드(2021) 7.01 API 오용 — DNS lookup에 의존한 보안결정

## 실행/컴파일 방법
```bash
javac Vulnerable.java Secure.java
java Vulnerable   # 역방향 DNS 이름으로 신뢰 판정(위조 가능)
java Secure       # 원시 IP 허용목록으로 판정(위조 불가)
```

## 참고
- CWE-350, KISA 소프트웨어 개발보안 가이드(2021.12) API 오용 항목
- 역방향 DNS(PTR) 레코드의 신뢰성 한계
