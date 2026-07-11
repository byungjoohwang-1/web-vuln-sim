# Private 배열에 Public 데이터 할당 (CWE-496 / KISA 6.04 캡슐화)

## 제목
- 약점명: Private 배열에 Public 데이터 할당
- CWE: CWE-496 (Public Data Assigned to Private Array-Typed Field)
- KISA 개발보안 가이드(2021) 항목: 6.04 (캡슐화)

## 개념
외부에서 전달받은 배열 참조를 그대로 private 필드에 저장하면, 호출자는
여전히 그 배열의 참조를 가지고 있다. 이후 외부에서 배열을 수정하면 객체
내부 상태가 함께 바뀌어 캡슐화가 무너진다. CWE-495(반환)의 반대 방향 문제다.

## 취약 원인
- `public void setPermissions(int[] p) { this.permissions = p; }` 처럼 참조를 그대로 저장한다.
- 세터 호출 후에도 외부가 같은 배열을 조작할 수 있어 내부 값이 뒤바뀐다.

## 영향
- 권한 배열, 설정값 등 내부 상태가 외부에서 변조된다.
- 권한 우회, 검증 우회 등 보안 결정이 왜곡될 수 있다.

## 안전한 코딩
- 세터/생성자에서 입력 배열을 복사해 저장한다: `this.permissions = p.clone();` 또는 `Arrays.copyOf(p, p.length)`.
- 조회 시에도 복사본을 반환해 유출을 막는다.
- null 입력은 빈 배열 등 안전한 기본값으로 정규화한다.

## 취약 vs 안전 차이
- 취약: `this.permissions = p;` → 외부 참조 공유, 원본 조작이 내부에 반영됨.
- 안전: `this.permissions = p.clone();` → 복사본 저장, 외부 조작과 격리.

## CWE·KISA 매핑
- CWE-496: Public Data Assigned to Private Array-Typed Field
- KISA 개발보안 가이드(2021) 6.04 캡슐화 — Private 배열에 Public 데이터 할당

## 실행/컴파일 방법
```bash
javac Vulnerable.java Secure.java
java Vulnerable   # 외부 배열 조작 → 내부 권한 우회(false→true)
java Secure       # 복사본 저장 → 내부 권한 유지(false)
```

## 참고
- CWE-496, KISA 소프트웨어 개발보안 가이드(2021.12) 캡슐화 항목
- 방어적 복사(Defensive Copy) 관용구
