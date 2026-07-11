# Public 메소드로부터 반환된 Private 배열 (CWE-495 / KISA 6.03 캡슐화)

## 제목
- 약점명: Public 메소드로부터 반환된 Private 배열
- CWE: CWE-495 (Private Data Structure Returned From A Public Method)
- KISA 개발보안 가이드(2021) 항목: 6.03 (캡슐화)

## 개념
자바에서 배열은 객체 참조다. private 배열 필드의 참조를 public 메소드가
그대로 반환하면, 호출자는 반환된 배열을 통해 내부 상태를 직접 수정할 수
있다. 결과적으로 캡슐화가 무너진다.

## 취약 원인
- `public int[] getScores() { return this.scores; }` 처럼 내부 배열 참조를 그대로 반환한다.
- 호출자가 반환 배열의 원소를 바꾸면 원본 필드(this.scores)도 함께 바뀐다.

## 영향
- 객체의 불변식(예: 검증된 값, 정렬 상태)이 외부에서 깨진다.
- 의도치 않은 상태 오염으로 계산 오류·보안 판단 오류가 발생한다.

## 안전한 코딩
- 반환 시 방어적 복사본을 준다: `return this.scores.clone();` 또는 `Arrays.copyOf(...)`.
- 컬렉션이라면 `Collections.unmodifiableList(...)` 같은 불변 뷰를 반환한다.
- 생성자/세터에서도 입력 배열을 복사해 외부 참조와 끊는다.

## 취약 vs 안전 차이
- 취약: `return this.scores;` → 내부 참조 유출, 외부 수정이 원본에 반영됨.
- 안전: `return this.scores.clone();` → 복사본 반환, 원본은 불변.

## CWE·KISA 매핑
- CWE-495: Private Data Structure Returned From A Public Method
- KISA 개발보안 가이드(2021) 6.03 캡슐화 — Public 메소드로부터 반환된 Private 배열

## 실행/컴파일 방법
```bash
javac Vulnerable.java Secure.java
java Vulnerable   # 반환 배열 조작 → 내부 합계가 바뀜(240→150)
java Secure       # 복사본 반환 → 내부 합계 유지(240)
```

## 참고
- CWE-495, KISA 소프트웨어 개발보안 가이드(2021.12) 캡슐화 항목
- 방어적 복사(Defensive Copy) 관용구
