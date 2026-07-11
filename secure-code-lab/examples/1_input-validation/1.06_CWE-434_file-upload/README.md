# 위험한 형식 파일 업로드 (Unrestricted File Upload) · CWE-434 · KISA 4.6

## 개념
서버가 업로드 파일의 형식·확장자·저장 위치를 제대로 통제하지 않을 때 발생한다. 공격자가 실행 가능한 파일(웹셸 등)을 올려 서버에서 실행시키면 시스템을 장악할 수 있다.

## 취약 원인
- 확장자·MIME 타입 검증 없이 업로드를 허용했다.
- 클라이언트가 보낸 원본 파일명(`getOriginalFilename()`)을 그대로 저장 경로로 사용했다.
- 업로드 파일을 웹에서 직접 실행 가능한 디렉터리에 저장했다.

## 공격 시나리오
- `shell.jsp`/`cmd.php` 웹셸을 업로드해 URL로 접근·실행한다.
- 이중 확장자(`img.jpg.jsp`)나 널바이트 트릭으로 검증을 우회한다.
- 원본 파일명에 `../` 를 넣어 다른 경로에 파일을 배치한다.

## 안전한 코딩(핵심 조치)
- 확장자 화이트리스트(`ALLOWED_EXT`)와 MIME 타입을 함께 검증한다.
- 원본 파일명을 신뢰하지 않고 서버가 생성한 안전한 이름(UUID 등)으로 저장한다.
- 업로드 파일은 웹에서 직접 실행되지 않는 영역에 저장한다.
- 파일 크기 제한, 실행 권한 제거, 콘텐츠 검사를 병행한다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 형식 검증 | 없음 | 확장자 + MIME 이중 검증 |
| 저장 파일명 | 원본 그대로 | UUID 등 안전한 이름 |
| 저장 위치 | 웹루트 | 실행 불가 영역 |

## CWE·KISA 매핑
- CWE-434: Unrestricted Upload of File with Dangerous Type
- KISA 소프트웨어 개발보안 가이드(2021) 4장 입력검증 및 표현 — 위험한 형식 파일 업로드

## 실행/컴파일 방법
```
javac Vulnerable.java
javac Secure.java

python bugfinder/bugfinder.py examples/1_input-validation/1.06_CWE-434_file-upload
```

## 참고
- CWE-434: https://cwe.mitre.org/data/definitions/434.html
- OWASP File Upload Cheat Sheet
