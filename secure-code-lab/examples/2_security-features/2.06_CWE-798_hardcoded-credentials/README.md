# 하드코드된 중요정보 (Use of Hard-coded Credentials) — CWE-798 / KISA 2.6

## 개념
비밀번호, API 키, 암호화 키 같은 인증정보를 소스코드에 문자열로 직접 박아 넣어,
소스·산출물 노출 시 그대로 유출되는 약점이다. 값 교체도 재빌드·재배포를 요구해
사고 대응이 느려진다.

## 취약 원인
- `String password = "..."`처럼 비밀정보를 소스 상수로 둔다.
- 버전관리 저장소에 실수로 커밋되거나, 배포 산출물을 디컴파일하면 노출된다.
- 여러 환경(개발/운영)이 같은 하드코딩 값을 공유해 노출 범위가 커진다.

## 공격 시나리오
1. 공격자가 유출된 소스나 APK/JAR를 디컴파일한다.
2. 하드코딩된 DB 비밀번호·API 키를 그대로 추출한다.
3. 해당 자격으로 DB/외부 API에 직접 접근해 데이터를 탈취한다.

## 안전한 코딩
- 비밀정보는 환경변수, 시스템 속성, 시크릿 관리 서비스(Vault, KeyStore 등)에서 읽는다.
- 소스·저장소에는 비밀정보를 두지 않고, `.gitignore`로 설정 파일을 제외한다.
- 키 회전(rotation)이 가능하도록 외부 주입 구조를 만든다.

## 취약 vs 안전 차이
| 구분 | 취약(Vulnerable) | 안전(Secure) |
|------|------------------|--------------|
| 저장 위치 | 소스코드 상수 | 환경변수/시크릿 저장소 |
| 유출 경로 | 소스·산출물 | 소스에는 값 없음 |
| 키 교체 | 재빌드 필요 | 외부 값만 교체 |

## CWE·KISA 매핑
- CWE-798: Use of Hard-coded Credentials
- KISA 소프트웨어 개발보안 가이드(2021.12) 2.6 하드코드된 중요정보

## 실행/컴파일 방법
```bash
javac Vulnerable.java && java Vulnerable
# Secure 실행 전 환경변수 설정
export PAYMENT_API_KEY=sk_test_xxx
javac Secure.java && java Secure
```

## 참고
- CWE-798: https://cwe.mitre.org/data/definitions/798.html
- KISA 소프트웨어 개발보안 가이드(2021.12)
