# 주석문 안에 포함된 시스템 주요정보 (Information Exposure Through Comments) — CWE-615 / KISA 2.13

## 개념
소스 코드 주석은 실행에는 영향을 주지 않지만, 배포 산출물(JAR/맵 파일/프론트엔드 번들 등)에
그대로 남거나 소스가 유출될 경우 공격자에게 유용한 정보가 된다. 주석에 접속 문자열, 비밀번호,
API 키, 내부 IP/경로 같은 시스템 주요정보를 남기면 그 자체가 취약점이 된다.

## 취약 원인
- 개발 편의를 위해 DB 접속 정보·비밀번호를 주석에 메모한다.
- `// jdbc:mysql://prod-...`, `// db password: ...` 처럼 실제 값을 남긴다.
- 코드 리뷰/배포 전 정리 과정에서 주석을 제거하지 않는다.

## 공격 시나리오
1. 공격자가 소스 저장소 유출, 디컴파일, 프론트엔드 소스맵 등으로 코드를 확보한다.
2. 주석에서 운영 DB 접속 문자열과 비밀번호, API 키를 읽는다.
3. 별도의 취약점 없이도 그대로 인프라에 접근한다.

## 안전한 코딩
- 주석에는 "무엇을 왜 하는지"만 적고, 실제 비밀값·접속정보는 절대 적지 않는다.
- 접속 정보와 자격증명은 환경변수·보안 저장소(Vault)에서 로드한다.
- 배포 파이프라인에서 민감 문자열 스캐닝(시크릿 스캐너)을 수행한다.
- 이 예제의 안전 코드처럼 주석과 코드 어디에도 실제 값이 남지 않게 한다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable) | 안전(Secure) |
|------|------------------|--------------|
| 주석 내용 | `// db password: ...`, `// jdbc:...` | 의도만 기술, 값 없음 |
| 접속정보 | 주석에 노출 | 환경변수/설정에서 로드 |
| 유출 시 위험 | 즉시 인프라 접근 | 노출 정보 없음 |

## CWE·KISA 매핑
- CWE-615: Inclusion of Sensitive Information in Source Code Comments
- KISA 소프트웨어 개발보안 가이드(2021) 보안기능 항목 2.13 주석문 안에 포함된 시스템 주요정보

## 실행/컴파일 방법
```bash
javac Vulnerable.java && java Vulnerable
javac Secure.java && java Secure
```

## 참고
- CWE-615 Inclusion of Sensitive Information in Source Code Comments
- KISA 소프트웨어 개발보안 가이드(2021.12)
- OWASP Secrets Management Cheat Sheet
