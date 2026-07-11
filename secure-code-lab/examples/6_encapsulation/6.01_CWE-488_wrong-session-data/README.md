# 잘못된 세션에 의한 데이터 정보 노출 (CWE-488 / KISA 6.01 캡슐화)

## 제목
- 약점명: 잘못된 세션에 의한 데이터 정보 노출
- CWE: CWE-488 (Exposure of Data Element to Wrong Session)
- KISA 개발보안 가이드(2021) 항목: 6.01 (캡슐화)

## 개념
서버 애플리케이션은 다수의 사용자 요청을 동시에 처리한다. 서블릿/컨트롤러
인스턴스는 일반적으로 스레드 간에 공유되므로, 사용자별(요청별) 데이터를
static 필드나 인스턴스 필드에 저장하면 하나의 저장 공간을 여러 요청이
공유하게 된다. 그 결과 한 사용자의 데이터가 다른 사용자의 세션에서 노출된다.

## 취약 원인
- 로그인 사용자 정보를 `private static User currentUser` 에 보관한다.
- static 필드는 클래스당 단 하나뿐이라 모든 스레드/요청이 같은 값을 읽고 쓴다.
- A 사용자가 값을 넣은 뒤 B 사용자의 요청이 그 값을 덮어쓰거나 그대로 읽는다.

## 영향
- 다른 사용자의 계정 정보, 카드번호 등 민감정보가 엉뚱한 세션에 노출된다.
- 권한/식별 혼선으로 인한 무단 조회·조작이 발생할 수 있다.
- 부하가 높을수록(동시 요청이 많을수록) 재현 확률이 커진다.

## 안전한 코딩
- 사용자별 상태는 공유 필드가 아니라 요청/세션 범위에 저장한다.
  - 웹: `request.getSession().setAttribute(...)` / `request.getAttribute("user")`
  - 순수 자바: `ThreadLocal` 로 스레드마다 독립된 저장소를 사용하고, 처리 종료 시 `remove()` 로 정리한다.
- 상태를 공유해야 한다면 불변 객체 + 명시적 동기화로 설계하고, 사용자 식별값을 절대 공유하지 않는다.

## 취약 vs 안전 차이
- 취약: `private static User currentUser;` → 전역 1개 슬롯을 모두가 공유.
- 안전: `private static final ThreadLocal<User> CURRENT` → 스레드(요청)마다 격리, `remove()` 로 정리.

## CWE·KISA 매핑
- CWE-488: Exposure of Data Element to Wrong Session
- KISA 개발보안 가이드(2021) 6.01 캡슐화 — 잘못된 세션에 의한 데이터 정보 노출

## 실행/컴파일 방법
```bash
javac Vulnerable.java Secure.java
java Vulnerable   # alice 화면에 bob 정보가 뜨는 세션 혼선 재현
java Secure       # 각 사용자는 자기 정보만 확인
```

## 참고
- CWE-488, KISA 소프트웨어 개발보안 가이드(2021.12) 캡슐화 항목
- 서블릿 컨테이너의 스레드 모델과 ThreadLocal 정리 규칙
