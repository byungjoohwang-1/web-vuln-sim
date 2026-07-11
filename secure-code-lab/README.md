# 🛡️ Secure Code Lab

**KISA 『소프트웨어 개발보안 가이드(2021)』 구현단계 보안약점 49종**을 실제로 컴파일·실행할 수 있는
**취약 코드 / 안전 코드 쌍**과, 이를 스스로 탐지하는 **버그 파인더(경량 SAST)** 로 학습하는 로컬 실습 키트다.

> 웹 시뮬레이터([vuln-sim.web.app](https://vuln-sim.web.app))가 "브라우저에서 공격을 체험"하는 도구라면,
> 이 Secure Code Lab 은 "IDE에서 실제 소스코드를 열어 약점을 찾아내고 고치는" 도구다.

---

## 무엇이 들어있나

```
secure-code-lab/
├─ README.md                ← 이 문서
├─ INDEX.md                 ← 49개 약점 전체 색인(표)
├─ .vscode/                 ← VS Code 권장 확장/작업(F1▸Tasks: Run Task ▸ Bug Finder)
├─ bugfinder/
│   ├─ bugfinder.py         ← 버그 파인더 (Python, 무설치·표준 라이브러리만)
│   ├─ rules.json           ← 49개 탐지 규칙 (danger/sanitizer 정규식)
│   └─ README.md            ← 파인더 동작 원리
└─ examples/
    ├─ 1_input-validation/  (17)  입력데이터 검증 및 표현
    ├─ 2_security-features/ (16)  보안기능
    ├─ 3_time-and-state/    (2)   시간 및 상태
    ├─ 4_error-handling/    (3)   에러처리
    ├─ 5_code-error/        (5)   코드오류
    ├─ 6_encapsulation/     (4)   캡슐화
    └─ 7_api-abuse/         (2)   API 오용
```

각 약점 폴더(`<번호>_<CWE>_<약점명>/`)에는 3개 파일이 있다.

| 파일 | 내용 |
|---|---|
| `Vulnerable.java` / `Vulnerable.c` | **정탐** — 실제 보안약점이 있는 코드 |
| `Secure.java` / `Secure.c` | **안전** — 같은 기능을 안전하게 고친 코드 |
| `README.md` | 개념 · 취약 원인 · 공격 시나리오 · 안전한 코딩 · CWE/KISA 매핑 · 실행법 |

전체 목록은 **[INDEX.md](INDEX.md)** 참고. (Java 44종, C 5종 — 정수오버플로우·버퍼오버플로우·포맷스트링·해제된자원사용·초기화되지않은변수)

---

## 설치 & 실행

### 1) 필요한 것
- **Python 3.8+** — 버그 파인더 실행용 (외부 패키지 불필요)
- (선택) **JDK 17+** — Java 예제 컴파일용 (`javac`)
- (선택) **GCC/Clang** — C 예제 컴파일용 (`gcc`)
- (권장) **VS Code** + 아래 확장

### 2) 버그 파인더 실행
```bash
cd secure-code-lab

# examples/ 전체 스캔 (취약 코드가 모두 탐지되고 안전 코드는 깨끗해야 함)
python bugfinder/bugfinder.py

# 특정 폴더/파일만 스캔
python bugfinder/bugfinder.py examples/1_input-validation/1.01_CWE-89_sql-injection/Vulnerable.java

# ★ 본인이 작성한 코드도 스캔 가능
python bugfinder/bugfinder.py /path/to/your/src

# 예제 자가검증 (정탐/오탐 0 확인 — CI용)
python bugfinder/bugfinder.py --selftest

# JSON 출력 (다른 도구 연동)
python bugfinder/bugfinder.py --json examples/2_security-features
```

> **Windows PowerShell 인코딩**: 콘솔이 한글에서 깨지면 `chcp 65001` 또는
> `$env:PYTHONIOENCODING="utf-8"` 후 실행. (파인더가 UTF-8 출력을 자동 설정하지만 예비책)

### 3) 예제 직접 컴파일/실행
```bash
# Java (폴더에서 Vulnerable + Secure 함께 컴파일)
cd examples/1_input-validation/1.01_CWE-89_sql-injection
javac Vulnerable.java Secure.java

# C
cd examples/5_code-error/5.03_CWE-416_use-after-free
gcc Vulnerable.c -o vuln && ./vuln
```
> 일부 Java 예제는 `javax.servlet` 등 웹 API 타입을 사용한다. 개념 학습·파인더 스캔에는 컴파일이 필요 없으며,
> 직접 컴파일하려면 해당 폴더 README의 안내대로 `servlet-api.jar` 를 클래스패스에 추가한다.

---

## 학습 흐름 (권장)

1. **INDEX.md** 에서 관심 약점을 고른다.
2. 폴더의 **README.md** 로 개념과 공격 시나리오를 읽는다.
3. **`Vulnerable`** 를 열고, 어디가 취약한지 스스로 찾아본다.
4. `python bugfinder/bugfinder.py <그 폴더>` 로 파인더가 같은 지점을 짚는지 확인한다.
5. **`Secure`** 와 비교해 무엇이 어떻게 바뀌었는지 확인한다.
6. 스스로 취약 코드를 고쳐 파인더가 **깨끗**하다고 할 때까지 반복한다.

---

## 버그 파인더는 어떻게 동작하나

각 규칙은 **위험 싱크(danger)** 정규식과 **완화 지표(sanitizer)** 정규식을 갖는다.
danger 가 매칭되고 sanitizer 가 없으면 약점으로 보고하고, sanitizer 가 있으면 안전한 것으로 보고 억제한다(오탐 감소).
자세한 원리와 한계는 [bugfinder/README.md](bugfinder/README.md) 참고.

> ⚠️ 이 파인더는 **학습용 경량 패턴 분석기**다. 정탐률/오탐률을 손으로 검증한 교육 예제에 최적화돼 있으며,
> 실무에서는 상용/오픈소스 정적분석기(SonarQube, Semgrep, CodeQL, Fortify 등)를 병행해야 한다.

---

## 참고 자료
- KISA 『소프트웨어 개발보안 가이드』 (2021.12)
- KISA 『소프트웨어 보안약점 진단가이드』 (2021)
- MITRE **CWE** (Common Weakness Enumeration)

> 본 키트의 예제 코드와 설명은 위 가이드의 **개념을 재구성**해 자체 작성한 것으로, 원문을 그대로 옮기지 않았다.
> CWE 번호와 KISA 항목명·번호는 참조용으로 인용한다.

---

*Secure Code Lab — WEB-VULN-SIM 프로젝트의 오프라인 실습 키트*
