# 🎓 WEB-VULN-SIM — KISA SW보안약점 진단원 학습 포털 (현황 문서)

> 본 문서는 프로젝트의 **현재 구축 상태**와 작업 규약을 기술한다. (최종 갱신: 2026-06-22)
> Firebase 정적 호스팅 기반의 한국어 보안 교육 포털이며, 핵심 앱은 `secure-dev-academy`(진단원 이수시험 대비)다.

---

## 1. 배포 · 진입 구조

* **배포**: `firebase deploy --only hosting --project vuln-sim --account mibbeuda@gmail.com`
  → **https://vuln-sim.web.app** (소유: mibbeuda@gmail.com / Spark 무료 플랜)
  * `public/` 만 서빙된다. `books/`(저작권 PDF 원문)·`_gen/`(생성기)은 **배포되지 않는다.**
  * 로그인/백엔드 없음(클라이언트 + localStorage 단독 구동). Cloud Functions=Blaze 유료라 미사용.
* **진입**: `index.html`(스플래시) → ① `vuln-hub.html`(취약점 학습 허브) ② `secure-dev-portal.html`(개발보안 학습) ③ `secure-dev-academy.html`(진단원 학습 센터, 플래그십) ④ `coding-standards.html`(C/C++ 코딩 표준 레퍼런스, TRACK 03).

---

## 2. secure-dev-academy — 진단원 학습 센터 (플래그십)

`_gen/gen_academy.py` 가 단일 HTML로 생성한다. 모든 진도/기록은 localStorage(NS `sda_`).

### 학습 모드(탭)
| 탭 | 내용 |
| :-- | :-- |
| 📊 대시보드 | 진도·게이미피케이션(XP/레벨/스트릭/배지)·12주 활동 히트맵·취약 유형 Top3·상용 SAST 비교 |
| 🗺️ 학습 경로 | 기초→개념→플래시→1교시→2교시→오답복습 가이드 커리큘럼 + 다음 추천 단계 |
| 🧱 기초 과정 | Java·C·Python 보안 기초 18카드 |
| 📖 개념 학습 | 49개 보안약점 개념카드(KISA Java/Python 코드쌍) + 7대 유형 개요 |
| 🃏 플래시카드 | 개념 인출 암기 |
| 📝 1교시 이론 | 객관식·OX·단답 **132문항**(QUIZ 40 + THEORY 92). **"실전 30문항(객관식)"** 프리셋 |
| 🧪 2교시 실무 | 코드 정·오탐 판별 + 서술형 채점 **78문항**. SARIF 2.1.0 내보내기 |
| 📐 설계 진단 | **복합서술형 12 시나리오** — 설계 산출물 검토→진단보고서(분류·Y/N·현황·개선) 작성 |
| 💻 코드 실행 | Monaco + Pyodide(Python)/Piston(Java·C) 온라인 실행 데모 9종 |
| ❌ 오답노트 | SM-2 간격 반복(SRS) 복습 |

### 채점 엔진(핵심: "검증 연극" 차단)
* **LASHR**(경량 구조 휴리스틱): 46개 약점에 대해 정규식 구조 패턴(all/any/none) 검증. 모범답안은 반드시 통과하도록 harness가 강제.
* **클라이언트 AST**(tree-sitter, 무료·폴백 안전): 채점 전 주석을 AST로 정확히 제거(문자열 속 `//`·`#` 오탐 방지). 로딩 실패 시 정규식으로 자동 폴백.
* 개선코드는 구조 통과 시 만점, 키워드만 있고 구조 미확인 시 상한 캡. 주석에만 키워드를 넣는 우회는 0점.

### 게이미피케이션(전부 localStorage, 무료)
XP·레벨 곡선·일일목표(50XP)·연속학습 스트릭·12주 히트맵·배지 13종. 농사 방지(개념/플래시는 1회만 적립).

---

## 3. 2026 이수시험 정합성 (안내서 기준)

`books/(공지용) 2026년 SW보안약점 진단원 이수시험 안내서.pdf` 분석 반영(텍스트: `books/_extract/exam_notice_2026.txt`).

* **1교시 이론**: 60분 · **30문항 전면 객관식**(OMR, 2025년~) · 가중치 **40%** · 과락 60점.
* **2교시 실습**: 100분 · **15문항 서술형**(정·오탐 분석 + **복합서술형 설계 진단보고서**) · 가중치 **60%** · 과락 60점.
* **합격**: 종합 70점 이상. 시험 중 'SW 보안약점 기준 명칭' 제공.
* 아카데미는 이 구조를 탭 상단 안내 패널로 명시하고, 실전 객관식·설계 진단 모드로 대비한다.

---

### C/C++ 코딩 표준 레퍼런스 (`coding-standards.html`)
* `_gen/gen_standards.py` 가 단일 HTML로 생성. 규칙 데이터는 표준별 모듈 `std_misrac`·`std_misracpp`·`std_certc`·`std_certcpp`·`std_autosar`의 `RULES`(스키마 `{id,cat,title,bad,good,why}`)에서 import. 각 표준 모듈은 **파트 분리**(`std_<key>_p1~p3.py`)를 병합한다(예: `std_misrac.py = p1+p2+p3`).
* 5대 표준 **총 506룰**(MISRA C:2012 127 · MISRA C++:2023 94 · CERT C 97 · CERT C++ 67 · AUTOSAR C++14 121). 탭·표준내 검색·위반↔준수 코드 토글 UI.
* **KISA 매칭 없음**(사용자 요청). 규칙 ID·제목·분류 체계만 인용, **코드 예제·해설은 전부 자체 작성**(규범 원문 비복제). 페이지 내 viewport+@media 자체 포함(파이프라인 불필요, 독립 생성).
* 재생성: `cd _gen && PYTHONIOENCODING=utf-8 python gen_standards.py`.
* 주의: 코드 필드는 raw 삼중따옴표 `r"""..."""`로 작성(끝에 `"`/백슬래시 금지). `why`/`title`는 일반 문자열이라 백슬래시 이스케이프(`\x` 등) 주의.

## 4. 콘텐츠 파이프라인 (`_gen/`)

* **생성**: `python gen_academy.py` → `public/secure-dev-academy.html`.
  데이터는 모듈 분리: `specs_academy.py`(CONCEPTS 49), `specs_code49.py`(CODE49), `specs_academy_practical.py`(PRACTICAL 78·THEORY 92, 하위 `_practical_new`·`_prac_cov1~3`·`_prac_ext`·`_prac_exam2412` + `_theory_ext`·`_theory_exam`·`_theory_exam2`·`_theory_exam3` 병합), `_basics`·`_tools`·`_runnable`·`_design`(DESIGN 12).
* **빌드 일원화**: `python build.py` = gen_academy → inject_refcard → **inject_responsive** → node 검증 하니스 → 회귀(_regression). (Windows 콘솔은 `PYTHONIOENCODING=utf-8`)
* **검증**: `node _validate_academy.js`(DOM-shim 위 단위검증 — 데이터 스키마·채점·SRS·게이미피케이션·SARIF·설계진단). 통과 기준: 채점 440/440 · exCorrect 132/132 · 회귀 PASS.
* **다른 도메인**: `gen_securecode`(03_code_*), `gen_fin`(금융 43), infra 생성기. **재생성 후엔 `inject_refcard`·`inject_responsive` 재실행 필수**(생성 시 주입물 소실).

### 신규 문항 작성 규칙(harness 강제)
* 정탐 `safeCode`는 LASHR all/any/none 통과必, `safeCodeKeywords`는 주석 제거 후에도 코드에 실재하는 토큰.
* TP `negKw`는 "안전한 코드"·"오탐" 포함하되 모범 서술/해설과 비충돌(false-penalty 0). FP `negKw[0]`는 해설·reasonKeywords에 없는 단정형.

---

## 5. 작업 규약 (제약)

* **저작권**: `books/`의 KISA PDF는 원문이다. 개념 재구성으로만 인용하고 **원문 verbatim 복사 금지**. 코드 예제는 KISA 가이드에 충실하게(예: Python eval/isalnum은 가이드 원문 유지 — 임의로 ast.literal_eval로 바꾸지 않음).
* **무료 유지**: Firebase Spark 범위 내. 서버사이드 채점·관리자 자동메일 등 Cloud Functions(Blaze) 필요 기능은 미도입.
* **반응형**: 전 페이지 viewport + `@media` 보강 완료(`inject_responsive.py`). 신규/재생성 페이지도 파이프라인이 보강.
* 배포 전: 빌드+검증 통과 → 깨진 링크/미치환 `__TOKEN__` 0 확인 → 배포.

---

## 6. 상용화 로드맵 — 진행 상태

원본 감사 보고서(B2B SaaS)의 과제별 현재 상태:

| 과제 | 상태 | 비고 |
| :-- | :-- | :-- |
| 콘텐츠 정확성·깊이(7대 유형·49약점·KISA 충실) | ✅ 완료 | 2·1교시 대폭 확충, 2024.12 기출·2026 안내서 반영 |
| 학습 설계(SRS·7유형 오답통계·게이미피케이션·학습경로) | ✅ 완료 | SM-2, XP/레벨/배지, 가이드 커리큘럼 |
| UX/모바일/접근성 | ✅ 완료 | 전 페이지 반응형, WCAG(스킵링크·aria-live·키보드) |
| 기술 건전성("검증 연극" 차단) | ✅ 완료 | LASHR 구조검증 + 클라이언트 AST(tree-sitter) |
| SARIF 표준 연동(과제4) | ✅ 완료 | 2교시 결과 SARIF 2.1.0 내보내기 |
| 복합서술형 설계 진단(2026 신규 유형) | ✅ 완료 | 📐 설계 진단 12 시나리오 |
| 로그인/클라우드 동기화 | ⏸ 제거됨 | 사용자 요청으로 Google 인증 제거(파일·규칙은 재활성 대비 보존) |
| 서버사이드 AST 채점(과제2) | ⛔ 보류 | Blaze 유료 필요 → 클라이언트 AST로 대체 |
| B2B 멀티테넌시 어드민(과제3)·콘텐츠 IP 보호(과제5) | ⛔ 보류 | 백엔드/로그인 전제 — 무료 범위 밖 |

> 참고: LASHR=Lightweight Advanced Structural Heuristic(생산용 SAST가 아닌 **교육용 구문 휴리스틱**, 정직히 명시). 본 포털은 강력한 학습 도구이며, 풀 상용 SaaS화는 백엔드(인증·서버채점·멀티테넌시) 도입이 잔여 마일스톤이다.
