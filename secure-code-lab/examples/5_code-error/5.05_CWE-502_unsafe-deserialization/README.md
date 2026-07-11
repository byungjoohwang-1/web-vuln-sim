# 신뢰할 수 없는 데이터의 역직렬화 (Unsafe Deserialization) · CWE-502 · KISA 5.05

## 개념
외부에서 받은 직렬화 데이터를 검증 없이 객체로 복원하는 약점이다. 자바 네이티브 역직렬화는 스트림에 기술된 임의 클래스의 객체를 되살리며, 그 과정에서 `readObject`/`readResolve` 같은 콜백이 실행되어 공격자가 제어 흐름을 탈취할 수 있다.

## 취약 원인
- `new ObjectInputStream(...).readObject()`를 신뢰 경계를 넘어온 바이트에 그대로 적용했다.
- 어떤 클래스가 복원될지 통제하는 필터(화이트리스트)가 없다.
- 그래프 깊이/참조 수 제한이 없어 자원 고갈 공격에도 노출된다.

## 영향
- 알려진 가젯 체인(예: Commons-Collections)을 담은 스트림으로 원격 코드 실행(RCE)이 가능하다.
- 대량의 중첩 객체로 메모리/CPU를 고갈시키는 DoS가 발생할 수 있다.
- 예상치 못한 타입 복원으로 애플리케이션 로직이 오염된다.

## 안전한 코딩
- `ObjectInputFilter` 화이트리스트를 만들어 `setObjectInputFilter`로 적용하고, 허용 클래스 외에는 모두 거부(`!*`)한다.
- `maxdepth`/`maxrefs`로 그래프 크기를 제한한다.
- 가능하면 네이티브 직렬화를 피하고 JSON 등 데이터 포맷 + 스키마 검증(예: Jackson `readValue` + 타입 제한)을 사용한다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.java) | 안전 (Secure.java) |
|------|------------------------|---------------------|
| 클래스 통제 | 없음 | `ObjectInputFilter` 화이트리스트 |
| 필터 적용 | 없음 | `setObjectInputFilter(ALLOWLIST)` |
| 크기 제한 | 없음 | `maxdepth`/`maxrefs` |

## CWE·KISA 매핑
- CWE-502: Deserialization of Untrusted Data
- KISA 소프트웨어 개발보안 가이드(2021) 5장 코드오류 — 신뢰할 수 없는 데이터의 역직렬화 (5.05)

## 실행/컴파일 방법
```
javac Vulnerable.java && java Vulnerable   # 필터 없는 무제한 역직렬화
javac Secure.java && java Secure           # 화이트리스트 필터 적용 (Java 9+ ObjectInputFilter)

# 프로젝트 루트에서 탐지 검증
python bugfinder/bugfinder.py examples/5_code-error/5.05_CWE-502_unsafe-deserialization
```

## 참고
- CWE-502: https://cwe.mitre.org/data/definitions/502.html
- Oracle: Serialization Filtering (`java.io.ObjectInputFilter`, JEP 290)
