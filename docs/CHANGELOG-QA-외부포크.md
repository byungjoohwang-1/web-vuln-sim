# QA 반영 변경 내역

- 기준 문서: `QA/vuln-sim-QA-소스대조-재검증-20260910.md`
- 작업일: 2026-09-13
- 원본: `web-vuln-sim/`
- 이 사본: `web-vuln-sim-fixed/`
- 검증: `python _gen/validate_build.py` 통과, Chromium 헤드리스 스모크 20페이지 + 기능 8건 통과

---

## 0. 한눈에

| 구분 | 건수 |
|:--|--:|
| 완전히 고친 항목 | 22 |
| 부분 조치 후 남긴 항목 | 3 |
| 새로 발견해 고친 결함 | 3 |
| 새로 만든 파일 | 9 |
| 삭제한 파일 | 2 |
| 이름을 바꾼 파일 | 3 |

**작업 중 새로 발견한 것 세 가지가 특히 중요하다.**

1. QA 보고서는 시뮬레이터 4개가 파손됐다고 적었지만, 전수 검사 결과 **6개**였다.
   `03_code_xss.html` 과 `07_fin-ssi.html` 이 추가로 같은 방식으로 죽어 있었다.
2. `sim-dast.html` 은 파싱 결함을 고친 뒤에도 동작하지 않았다.
   전역에 `var history=[]` 를 선언했는데 `window.history` 는 덮어쓸 수 없는 접근자라
   `history.push is not a function` 으로 죽었다. 스크립트가 먼저 깨져 있어서
   이 두 번째 결함이 그동안 드러나지 않았다.
3. Prism 하이라이터에는 원래부터 SRI 가 있었다. QA 보고서의
   "integrity 속성은 1건뿐"은 표본 20개 기준이라 과소 집계였다.
   실제로 빠져 있던 것은 **CSS 4종과 Monaco 로더, sql.js** 였다.

---

## 1. P1 치명 결함

### N-05 / I-04  빌드 스크립트가 만든 페이지 파손 6건

**증상** 해당 페이지에서 자바스크립트 소스가 본문 텍스트로 노출되고 기능이 전혀 동작하지 않음.

**원인** `_gen/inject_progress.py` 가 파일의 **첫 번째** `</body>` 를 치환했다.
시뮬레이터들은 자바스크립트 문자열 안에 mock HTML 응답을 담고 있고 그 문자열에
`</body></html>` 이 들어 있다. 그래서 주입 태그가 문자열 한가운데에 들어갔고,
태그에 포함된 `</script>` 가 HTML 파서 기준으로 스크립트 블록을 조기에 끝냈다.

| 파일 | 삽입 위치 | 문서 끝 | 비고 |
|:--|--:|--:|:--|
| `sim-dast.html` | 12,010 | 42,579 | QA 보고서가 관찰한 "본문 공백" |
| `sim-split.html` | 18,625 | 30,584 | |
| `sim-source-comments.html` | 12,208 | 15,937 | |
| `sim-ssrf.html` | 20,029 | 25,056 | |
| `03_code_xss.html` | 60,315 | 65,546 | **QA 보고서 미발견** |
| `07_fin-ssi.html` | 10,947 | 14,962 | **QA 보고서 미발견** |

**조치**
- 6개 파일에서 잘못 들어간 태그를 제거하고 문서 마지막 `</body>` 직전으로 옮겼다.
- `_gen/inject_progress.py` 를 `rfind('</body>')` 기반으로 교체했다.
- `_gen/validate_build.py` 에 재발 방지 검사 두 가지를 넣었다.
  주입 태그가 `<script>` 블록 내부에 있으면 실패, 블록 밖으로 자바스크립트가
  새어 나오면 실패.

### (신규) sim-dast.html 전역 변수 충돌

`var history=[]` 가 `window.history` 를 가리지 못해 실행 즉시 예외로 죽었다.
`reqHistory` 로 이름을 바꿨다. 헤드리스 브라우저로 워크스페이스 렌더를 확인했다.

### N-01  수료증 잠금 해제 백도어

`certificate.html` 에 `window.forceUnlockForDev()` 가 있었다. 콘솔에서 한 줄이면
개념 20개, 실습 20개, XP 500이 채워져 수료증이 나왔다. 버튼도 화면에 노출돼 있었다.

**조치** 함수와 버튼을 모두 제거. `validate_build.py` 가 `window.force*`,
`*ForDev` 패턴을 배포본에서 잡는다.

### N-02  수료증 자가검증이 위조를 막지 못함

`verify.html` 은 URL 에 담긴 데이터를 다시 SHA-256 으로 해싱해 첨부된 해시와 비교했다.
비밀 키가 없으므로 이름을 바꾸고 해시를 다시 계산하면 "무결성 확인됨"이 떴다.

**조치**
- 서버가 자기 키로 만든 HMAC-SHA256 서명으로 대체(`functions/index.js`).
- 검증 페이지 문구를 실제 보증 수준에 맞게 전면 수정.
  "무결성 확인됨 / 위·변조 없음" → "발급 사실 미확인 (링크 자체 일치)".
  "진위 확인됨" → "발급 확인됨 (서버 기록)".

### N-03  온라인 등록에 자격 검증이 없음

로그인만 하면 certId, 이름, 완료 수를 클라이언트가 정해 Firestore 에 직접 등록할 수 있었다.
수료번호도 완료 항목 첫 글자 코드 합에서 파생된 16진수 6자리라 충돌과 열거가 쉬웠다.

**조치**
- 발급을 `issueCertificate` Cloud Function 으로 옮겼다. 서버가 `users/{uid}` 진도를
  직접 읽어 판정하고, 수료번호를 128비트 난수로 발급한다.
- `firestore.rules` 에서 `certificates` 의 클라이언트 읽기와 쓰기를 모두 막았다.

### N-04  수료증 공개 조회로 실명 열람 가능

`allow get: if true` 라 무인증 단건 조회가 열려 있었고, 문서에 이름이 그대로 있었다.

**조치** 클라이언트 직접 조회를 차단하고 `verifyCertificate` 함수로만 조회한다.
응답에는 마스킹된 이름(`홍*동`)만 담는다.

### N-06  코딩 표준 IDE 가 사용자 코드를 외부로 전송

`coding-standards.html` 의 실행 버튼이 편집기 내용을 `wandbox.org` 로 POST 했다.
고지가 전혀 없었다.

**조치** 실행 전 확인 창으로 전송 사실을 알리고 취소할 수 있게 했다(세션당 1회).
`privacy.html` 과 `terms.html` 에도 명시했다.

### N-07  개인정보 처리방침과 이용약관 부재

Google 로그인으로 계정 정보를 받고 Firestore 에 학습 기록과 이름을 저장하면서
관련 문서가 한 건도 없었다.

**조치** `public/privacy.html`, `public/terms.html` 신설.
수집 항목, 목적, 보유 기간, 위탁과 국외 이전, 이용자 권리, 안전성 확보 조치를 표로 정리했다.
`index.html` 푸터와 공통 셸 푸터에서 링크한다.
데이터 삭제를 위한 `deleteMyData` Cloud Function 도 만들었다.

---

## 2. 등급이 올라간 항목

### I-03  SDLC 카드 키보드 조작 (재현 대기 → 확정, 수정 완료)

`<div class="phase" onclick="ph('req')">` 이고 파일 전체에 `tabindex` 가 0개였다.
키보드만으로는 단계 전환이 불가능했다(WCAG 2.1.1 실패).

**조치** `<button type="button">` 으로 교체하고 `aria-pressed`, `aria-controls` 를 부여했다.
`ph()` 가 선택 상태를 갱신하고, 상세 영역에 `aria-live="polite"` 를 건다.
헤드리스 브라우저에서 Tab 포커스와 Enter 전환을 확인했다.

### I-02  시험, 문제팩 시작 흐름 (C 가설 → B 원인 확인, 수정 완료)

부팅이 `window.onload` 에 걸려 있었다. 이 이벤트는 외부 자원이 전부 끝나야 발화하는데,
해당 페이지들은 Google Fonts 를 차단 방식으로 불러오고 627KB 의 데이터 스크립트를
동기 로드했다. 폰트가 느리거나 막힌 환경에서는 정적 화면만 그려지고 초기화가 오지 않는다.
오류 표시도 없어 "눌러도 아무 반응이 없는" 것처럼 보였다.

**조치**
- `js/boot-guard.js` 신설. DOM 준비 즉시 초기화하고, 5초 안전망을 두고,
  초기화가 예외로 죽으면 `role="alert"` 배너로 알린다. 9개 페이지에 적용.
- Google Fonts 링크 223개를 `media="print"` 로 바꿔 비차단으로 내려받고,
  `js/shell.js` 가 DOM 준비 후 `media="all"` 로 되돌린다.
  인라인 `onload` 핸들러를 쓰지 않아 CSP 강화와 충돌하지 않는다.
- 외부 CDN 을 전부 차단한 상태에서 `question-packs.html` 초기화를 확인했다.

---

## 3. 사실관계를 정정한 항목

### I-07  SRI 서술 정정

QA 보고서는 "Bootstrap 스크립트에 SRI 가 없다"고 적었으나 이미 적용돼 있었다.
또 "integrity 는 1건뿐"이라는 집계는 표본 20개 기준이었고, 전수로 보면
Prism 계열 167건에 이미 SRI 가 있었다.

**실제로 빠져 있던 것과 조치**

| 자원 | 페이지 수 | 조치 |
|:--|--:|:--|
| `prism-tomorrow.min.css` | 57 | SRI 추가 |
| `font-awesome/all.min.css` | 38 | jsDelivr npm 경로로 이동 후 SRI |
| `bootstrap.min.css` | 13 | SRI 추가 |
| `monaco-editor/loader.min.js` | 1 | jsDelivr npm 경로로 이동 후 SRI |
| `sql.js/sql-wasm.js` | 1 | SRI 추가 |
| `cdn.tailwindcss.com` | 1 | 로컬 `css/tailwind.css` 로 교체 |

해시는 npm 배포 tarball 에서 직접 계산했다. 방식의 정확성은
기존 HTML 에 있던 `bootstrap.bundle.min.js` 의 integrity 값과
npm 에서 계산한 값이 정확히 일치하는 것으로 검증했다.
검증 결과 **모든 외부 자원이 무결성 검증을 갖는다**(구글 폰트 제외, 브라우저별로
내용이 달라 SRI 불가).

### I-12  Verisign 표기는 오판정

`sim-sql.html` 의 "🔒 Verisign Secured" 는 사이트의 신뢰 배지가 아니라
SQL 삽입 시뮬레이터 안 가상 인터넷뱅킹 화면의 소품이다. 전체에서 1건뿐이다.
**허위 인증 표기로 제거할 대상이 아니다.** 다만 실존 상표를 모의 화면에 쓰는 것은
별개의 가벼운 문제이므로 `CLAUDE.md` 에 가상 브랜드를 쓰라는 규칙으로 남겼다.

---

## 4. P2 개선

### I-05  다국어 상태 불일치

실측: 82개 중 36개만 `documentElement.lang` 을 갱신, i18n 구현이 3종 혼재,
`manifest.json` 의 `lang` 이 `ko` 고정.

**조치** `js/shell.js` 가 전 페이지에서 `wvs_lang` 에 맞춰 `html lang` 을 동기화하고,
언어 전환 버튼 클릭과 다른 탭의 변경까지 따라간다. manifest 는 `lang` 제거 후
`dir: auto` 와 이중 언어 이름으로 바꿨다.

### I-06  PWA 설치 배너

`beforeinstallprompt` 를 받자마자 즉시 노출했고, 닫기 상태를 `sessionStorage` 에만
저장해 새 탭마다 다시 떴으며, safe-area 여백이 없어 CTA 를 가렸다.

**조치** 20초 지연 노출, 닫으면 `localStorage` 에 30일 스누즈, 설치 완료 시 영구 해제,
`env(safe-area-inset-*)` 적용, 배너에 `role="dialog"` 와 레이블 부여.

### I-08  접근성 랜드마크

실측: 82개 중 skip link 1, `<main>` 1, `<nav>` 0, `<header>` 6, `<footer>` 0.

**조치** `_gen/inject_shell.py` 로 전 405페이지에 skip link 와 포커스 스타일을
정적 주입하고, `js/shell.js` 가 본문, 내비게이션, 푸터 랜드마크를 부여한다.

레이아웃을 재배치하지 않는 방식을 택했다. 404개 페이지가 각자 손으로 맞춘
flex/grid 를 쓰고 있어 DOM 을 감싸면 깨진다. 기존 요소에 `role` 과 `id` 를 부여하는
방식이고, 보조기술은 정적 태그와 `role` 을 동일하게 취급한다.

### I-09  코딩 표준 텍스트 품질

PDF 합자가 깨져 단어 안에 공백이 들어간 것을 복원했다.
`defi ne` 6건, `identifi er` 12건, `qualifi ed` 6건, `ma cro` 6건, `unused ta g` 6건.
**코드 블록 안까지 번져 있었다**(`#def ine SIZE 4`). 복사해 쓰면 컴파일되지 않는다.

제작 공정을 그대로 드러내던 내부 메모 48건도 학습자 기준 문구로 바꿨다.
"PDF 원문에서 명시적인 준수 예제 코드는 분리되지 않아 표시하지 않습니다"
→ "이 규칙은 원문에 대응하는 준수 예제가 따로 실려 있지 않습니다. 위반 예시와
아래 설명으로 판단 기준을 익히세요."

`validate_build.py` 에 자기 검증형 합자 검사를 넣었다.
공백을 지운 형태가 같은 문서에 실제로 존재할 때만 분할로 판정하므로
`off the`, `diff comparison` 같은 정상 표현을 오탐하지 않는다.

### I-11  수치와 URL 단일화

| 항목 | 표기 | 실제 | 조치 |
|:--|--:|--:|:--|
| 인터랙티브 실습 | 319개+ | 369개 | 실제 값으로 수정 |
| 코딩 표준 규칙 | 500여종 | 1,117개 | 실제 값으로 수정 |

오타 URL 3건을 정규 URL 로 옮기고 `firebase.json` 에 301 리다이렉트를 넣었다.

- `03_code_hardedcode.html` → `03_code_hardcoded_credentials.html`
- `sim-hardedcode.html` → `sim-hardcoded-credentials.html`
- `03_code_inapporiate_auth.html` → `03_code_inappropriate_auth.html`

내부 링크 12개 파일을 일괄 갱신했고, 검증 게이트가 깨진 링크를 잡는다.

### I-10  대형 페이지

`coding-standards.html` 은 3.2MB, `<h3>` 1,117개, `<button>` 2,781개다.
**이번 사본에서는 분할하지 않았다.** 트리 탐색과 검색, 앵커 구조를 통째로
다시 설계해야 해서 회귀 위험이 크다. `CLAUDE.md` 의 미해결 과제로 남겼다.

### I-12  신뢰 표기와 학습 동선

- `og:image` 가 favicon SVG 라 SNS 카드에서 렌더되지 않았다.
  512px PNG 로 교체하고 `summary_large_image` 로 올렸다(405개 페이지).
- README 안에서 한국어 v0.5, 영어 v1.0 으로 갈라져 있던 버전을 통일했다.
- B2B 상용화 데모 탭이 학습자 화면에 조건 없이 노출됐다.
  `?view=saas` 또는 `wvs_role=staff` 일 때만 보이도록 게이트를 넣었다.
- 학습 페이지 306개에 이전-다음 이동과 진행 위치(`79 / 306`)를 추가했다.
- 공통 푸터에 버전, 전체 콘텐츠, 개인정보 처리방침, 이용약관을 넣었다.

---

## 5. 그 밖의 신규 항목

| ID | 내용 | 조치 |
|:--|:--|:--|
| N-08 | `config.js` 가 실제와 다른 프로젝트 ID(`vuln-sim-test`)를 가리키고 개인 메모 주석이 배포됨. 이를 쓰는 `sim-test.html` 의 버튼은 동작하지 않았고 sitemap 에도 등재 | 두 파일 삭제, 301 리다이렉트 |
| N-09 | `CLAUDE.md` 가 전혀 다른 프로젝트(주식 자동매매봇) 문서 | 이 프로젝트 기준으로 새로 작성 |
| N-10 | sitemap 에 관리, 운영, 검증 페이지와 개발 잔재가 등재 | sitemap 397개로 재생성, robots.txt 차단, `noindex` 메타와 `X-Robots-Tag` 추가 |
| N-11 | `my-progress.html` 이 존재하지 않는 `login.html` 로 링크 | 위젯 안내 문구로 교체 |
| N-12 | `sim_insufficient_session.html` 만 진도 엔진 미주입(파일명 구분자 차이) | 주입 완료, 판정식을 `sim_` 까지 확장 |
| N-13 | PWA 아이콘이 SVG 1종뿐, `lang` 고정 | 192, 512, maskable PNG 와 apple-touch-icon 생성, manifest 정비 |
| N-14 | 서비스 워커 캐시 이름이 `wvs-v1` 고정 | 배포 버전 반영, 새 자산 프리캐시 |
| N-15 | `question-admin.html` 이 공용 관리 콘솔처럼 보이나 실제로는 브라우저 로컬 전용 | 저장 범위를 화면에 명시, `noindex` |
| I-01 | AI 키 브라우저 저장 | 서버 프록시 경로 신설(기본 비활성), 로드 시 키를 입력창에 복원하던 동작 제거, 키 삭제 시 모델 키까지 정리, 경고 문구 강화 |

---

## 6. 보안 헤더와 CSP

`firebase.json` 의 CSP 는 `object-src`, `base-uri`, `frame-ancestors` 세 줄뿐이었다.
`default-src` 도 `script-src` 도 없었다.

**1단계로 인라인과 무관한 지시어부터 좁혔다.**
`default-src 'self'`, `img-src`, `font-src`, `style-src`, `connect-src`,
`worker-src`, `frame-src`, `form-action`, `manifest-src` 를 명시했다.
`Cross-Origin-Opener-Policy` 와 명시적 HSTS 도 추가했다.

`script-src` 에는 아직 `'unsafe-inline'` 이 남아 있다.
**인라인 이벤트 핸들러가 3,549개**라 한 번에 뺄 수 없다.
대신 이를 허용하지 않는 **보고 전용 정책(`Content-Security-Policy-Report-Only`)** 을
함께 배포해, 위반 로그를 보며 생성기 레벨에서 이벤트 위임 방식으로 전환한 뒤
조일 수 있게 했다.

Firestore 규칙에는 `match /{document=**} { allow read, write: if false; }` 기본 거부를
추가하고, 로그인자 누구나 모든 클래스를 읽을 수 있던 `classes` 의 `read` 를
`get` 만 허용하고 `list` 는 막도록 바꿨다.

---

## 7. 파일 변경 목록

**새로 만든 것**

```
public/privacy.html                 개인정보 처리방침
public/terms.html                   이용약관
public/js/shell.js                  공통 셸
public/js/boot-guard.js             부팅 보호
public/js/page-order.json           학습 순서 카탈로그 (306개)
public/icons/icon-192.png           PWA 아이콘
public/icons/icon-512.png
public/icons/icon-maskable-512.png
public/icons/apple-touch-icon.png
_gen/inject_shell.py                공통 셸 주입기
_gen/validate_build.py              배포 전 검증 게이트
CHANGELOG-QA.md                     이 문서
```

**삭제한 것**

```
public/sim-test.html                동작하지 않는 개발 잔재
public/config.js                    잘못된 프로젝트 ID + 개인 메모
```

**이름을 바꾼 것** (301 리다이렉트 있음)

```
03_code_hardedcode.html      -> 03_code_hardcoded_credentials.html
sim-hardedcode.html          -> sim-hardcoded-credentials.html
03_code_inapporiate_auth.html-> 03_code_inappropriate_auth.html
```

**크게 고친 것**

```
public/certificate.html    백도어 제거, 서버 발급 연동, 난수 수료번호
public/verify.html         서버 검증 연동, 보증 수준에 맞는 문구
public/auth-widget.js      issueCert / verifyCert / aiTutor / deleteMyData
public/ai-tutor.html       서버 프록시 우선, 키 복원 제거, 경고 강화
public/coding-standards.html  합자 복원, 내부 메모 정리, wandbox 고지
public/secure-dev-portal.html SDLC 카드 button 전환
public/secure-dev-academy.html B2B 탭 역할 게이트
public/js/pwa.js           설치 배너 지연, 영속 스누즈, safe-area
public/sw.js               캐시 버전, 프리캐시 목록
public/manifest.json       아이콘, 언어
public/sitemap.xml         397개로 재생성
public/robots.txt          관리 경로 차단
firebase.json              CSP, 보안 헤더, 리다이렉트, noindex
firestore.rules            수료증 잠금, 기본 거부
functions/index.js         Cloud Functions 4종 신설
CLAUDE.md                  프로젝트 문서 교체
README.md                  버전 통일, 사본 안내
_gen/inject_progress.py    rfind 기반, sim_ 지원
_gen/build.py              셸 주입과 검증 게이트 연결
```

전 페이지 공통 변경: skip link, `js/shell.js`, `og:image`, apple-touch-icon,
Google Fonts 비차단(223개), 외부 자원 SRI.

---

## 8. 배포 전 할 일

```bash
# 1. 검증
python _gen/validate_build.py          # 반드시 통과해야 함

# 2. 로컬 확인
python -m http.server 8099 --directory public

# 3. 수료증 서명 키 생성 (한 번만, 분실하면 기존 수료증 검증 불가)
openssl rand -hex 32
firebase functions:secrets:set CERT_SIGNING_KEY

# 4. 배포
firebase deploy --only firestore:rules
firebase deploy --only functions
firebase deploy --only hosting
```

**주의할 점**

- `functions/index.js` 의 `ALLOW_AI_PROXY` 는 기본 `false` 다.
  조직 키로 과금되므로 사용량 정책을 정한 뒤 켠다. 그때까지 AI 튜터는
  기존 개인 키 방식으로 동작한다(경고 문구는 강화돼 있다).
- Firestore 규칙 배포 후 기존 수료증(`certificates` 구버전 문서)은
  클라이언트에서 조회되지 않는다. 서버 함수는 Admin SDK 라 영향이 없지만,
  구버전 문서에는 서버 서명(`sig`)이 없어 검증에서 "기록 없음"으로 나온다.
  이행 기간 정책을 정한 뒤 재발급을 안내한다.
- `privacy.html` 의 문의 창구와 보유 기간은 운영 정책에 맞게 확정해야 한다.
  현재는 합리적인 기본값을 넣어 둔 상태다.

---

## 9. 이번에 손대지 않은 것

| 항목 | 이유 |
|:--|:--|
| `coding-standards.html` 분할 | 3.2MB 단일 페이지. 트리 탐색과 앵커 구조를 다시 설계해야 해 회귀 위험이 크다 |
| 인라인 이벤트 3,549개 외부화 | 생성기(`gen_*.py`) 전면 수정이 필요하다. 보고 전용 CSP 로 준비만 해 뒀다 |
| I-06 반응형 실측 대응 | 1280px 오버플로는 실제 렌더 측정이 필요하다. 여기서는 safe-area 와 배너 가림만 처리했다 |
| 코딩 표준 재배포 권리 | 법무 확인 사항. `terms.html` 에 상표와 제휴 관계 없음을 명시하는 선까지만 했다 |
| I-11 수치 출처 확인 | QA 보고서의 "DBMS 4", "전자금융 10", "코딩 표준 562" 는 현재 소스에서 재현되지 않는다. 어느 화면의 표기인지 특정이 필요하다 |

---

# 2차: 교육 콘텐츠 개선 (2026-09-13)

근거 문서 두 건을 반영했다.

- `WEB-VULN-SIM_웹-교육자료-개선-백로그.md` (W-02, W-03, W-06, W-08)
- `WEB-VULN-SIM_AI-교육-개편안.md` (A-01, A-03, A-04, A-05, A-06, A-07)

## 10. 수치를 한곳에서 센다 (W-06)

화면 배지에 손으로 적은 숫자가 있으면 콘텐츠가 늘고 줄 때마다 어긋난다.
실제 파일을 세어 레지스트리를 만들고, 화면은 그 값을 읽는다.

| 산출물 | 내용 |
|:--|:--|
| `_gen/gen_registry.py` | `public/` 을 훑어 `public/data/content-registry.json` 생성 |
| `public/js/registry.js` | `data-wvs-count`, `data-wvs-coverage`, `data-wvs-missing` 속성을 채움 |
| `validate_build.py` REGISTRY 검사 | 레지스트리가 실제 파일 수와 다르거나, HTML 대비값이 레지스트리와 어긋나면 실패 |

레지스트리가 센 값.

| 항목 | 값 |
|:--|--:|
| 학습 페이지 | 306 |
| 시뮬레이터 | 61 |
| 실습 총계 | 367 |
| 코딩 표준 규칙 | 1,117 |

`vuln-hub.html` 의 서브헤더 "(N개)" 표기도 실제 링크 수로 다시 쓰게 했다.
사이드바 배지는 원래부터 DOM 을 세고 있었으므로 그대로 뒀다.

## 11. 홍보 문구를 실제 동작에 맞춤 (W-02)

| 위치 | 이전 | 이후 |
|:--|:--|:--|
| `index.html` 트랙 1 | "369개 인터랙티브 실습" (손으로 적은 값) | 레지스트리 값 367 |
| `index.html` 트랙 1 | "신규: 시뮬레이터 28종" (근거 불명) | "Burp 스타일 DAST 콘솔 포함, 시뮬레이터 61종" |
| `index.html` 트랙 2, 4 | 49, 1,117 하드코딩 | 레지스트리 값 |
| `vuln-hub.html` UNIX | "완전 구성: U-01~U-61 41개" | 커버리지 배지와 미수록 목록 |

## 12. 리눅스 번호 공백을 숨기지 않는다 (W-03)

백로그의 선택지 C 를 골랐다. 없는 항목을 없다고 표시한다.

- `vuln-hub.html` UNIX 메뉴: `39/61 수록 (64%)` 배지와
  `미수록 항목 22개: U-07 ~ U-13, U-29 ~ U-33, U-48, U-51 ~ U-58, U-60 (준비 중)`
- `content-map.html`: 도메인 11개의 수록 현황 카드. 번호 체계가 있는 도메인은
  계획 범위 대비 비율을 막대로 보여 준다. DBMS 도 `22/26 (85%)` 로 드러났다.

허브에 없는 링크를 만들지 않았으므로 빈 화면이나 404 로 나가는 경로는 없다
(`validate_build.py` 의 DEAD-LINK 검사가 지킨다).

## 13. 실습 시작 안전 고지 (W-08, A-03)

`public/js/safety-notice.js` 를 공격형 실습 68개 페이지에 주입했다
(`_gen/inject_safety.py`, 멱등). 대상은 `sim-*`, 브리치 캠페인, 라이브 랩,
시큐어 코드 랩, AI 튜터, AI 채점기, 가드레일 연습장이다.

- 브라우저당 한 번만 뜬다. 확인하면 `wvs_safety_ack_v1` 에 남는다.
- 푸터의 "안전 고지 다시 보기" 로 언제든 다시 연다.
- Esc 로 닫히지 않고, "돌아가기" 와 "이해했습니다" 중 하나를 골라야 한다.
- 초점 순환(focus trap)과 `aria-modal` 을 넣었다.

## 14. AI 튜터: 키 없는 데모 모드 (A-01, A-02)

**먼저 고친 결함.** `ai-tutor.html` 에 `var history=[]` 가 전역에 있었다.
`window.history` 는 설정 불가 접근자라 이 선언은 조용히 무시되고,
첫 메시지에서 `history.push is not a function` 으로 대화가 죽었다.
`sim-dast.html` 에서 잡은 것과 같은 결함이 여기에도 있었다. `chatLog` 로 바꿨다.

**모드 세 가지.**

| 모드 | 키 | 동작 |
|:--|:--|:--|
| 데모 (기본) | 불필요 | `js/ai-demo.js` 가 사이트의 학습 자료로 규칙 기반 응답을 만든다. 외부 호출 없음 |
| 서버 프록시 | 불필요 | 로그인 후 Cloud Function 이 호출. 실패하면 데모로 내려간다 |
| 개인 키 | 필요 | 접힌 "고급 설정" 안으로 옮겼다. 저장 경고 강화 |

데모 엔진이 보장하는 것.

1. 주제 하나를 개념 → 진단 포인트 → 조치까지 설명한다.
2. 코드를 붙여넣으면 힌트 1단계(영역) → 2단계(줄) → 3단계(조치)로 올라간다.
3. 악용 요청은 거부하고 방어 관점 대안을 제시한다.

한계도 화면에 적었다. 규칙 기반이라 표현을 볼 뿐 의미를 보지 않는다.

## 15. 가드레일 연습장 신설 (A-06)

`public/ai-guardrail-lab.html`, 미션 5개, 규칙 기반 자동 채점.
API 키도 네트워크도 필요 없다.

| 미션 | 채점 기준 수 |
|:--|--:|
| 1. 위험 요청 거부 | 5 |
| 2. 힌트 1단계에서 3단계까지 | 5 |
| 3. AI가 만든 취약 코드 리팩터 | 6 |
| 4. 시크릿 탐지 | 4 |
| 5. 간접 프롬프트 주입 인지 | 4 |

점수 하나가 아니라 항목별 통과, 미달과 보완 힌트를 보여 준다.
각 미션에는 모범 답안을 함께 뒀고, 모범 답안이 자기 루브릭을 통과하는지
자체 검사로 확인했다(5개 전부 만점).

## 16. AI 트랙 허브와 학습 경로 (A-04, A-05, A-07)

| 산출물 | 내용 |
|:--|:--|
| `public/ai-hub.html` | Track 05. 진입점 4개와 학습 경로 전체 |
| `public/js/ai-track.js` | 26개 카드의 모듈, 난이도, 예상 시간, 선수 개념, 순서 |
| `public/js/ai-card.js` | 각 카드 상단 정보 띠와 이전-다음 |
| `_gen/inject_ai_meta.py` | 26개 카드에 주입 (멱등) |

모듈 7개로 묶었다: 기초(5), 응용(6), 적대적 ML(4), 딥페이크(3),
사고 재구성(2), 양자내성암호(3), 거버넌스(3). 전체 약 360분.

선수 개념은 이 사이트 안의 웹 약점 페이지를 가리킨다.
AI 보안은 새 취약점 목록이 아니라 익숙한 약점이 새 표면에서 다시 나타나는 것이라는
관점을 화면에서 유지하기 위해서다. 예: AI-06 불안전한 출력 처리 → XSS, 운영체제 명령 삽입.

진도 키는 `wvs_ai_track`, `wvs_ai_guardrail`, `wvs_ai_mode`, `wvs_ai_demo_progress` 로
`wvs_ai_*` 네임스페이스에 모았다(A-07). 전부 로컬 저장이고 서버로 보내지 않는다.

`index.html` 에 Track 05 카드를 추가했고, 훈련장 계열 8개 페이지 내비와
`vuln-hub.html` 의 AI 그룹 머리에 진입 링크를 달았다.

## 17. 2차 검증 결과

```
python _gen/validate_build.py        -> 통과 (407개 파일, 검사 9종)
```

헤드리스 브라우저 확인.

| 항목 | 결과 |
|:--|:--|
| 25개 대표 페이지 로드, 콘솔 오류 | 오류 0 |
| 데모 튜터 7턴 대화 (설명 → 진단 → 조치 → 리뷰 → 힌트 3단 → 거부) | 전부 의도대로 |
| 가드레일 미션 1, 4, 5 채점 | 전부 통과 판정 |
| AI 카드 메타 띠, 이전-다음, 첫 카드와 마지막 카드 경계 | 정상 |
| 허브 진행률이 방문 기록을 반영 | 3 / 26 로 갱신 확인 |
| 언어 전환(ko ↔ en) 후 레지스트리 배지 유지 | 유지됨 |
| 리눅스 커버리지 배지와 미수록 목록 | 39/61 (64%), 22개 |

## 18. 2차에서 손대지 않은 것

| 항목 | 이유 |
|:--|:--|
| Track D "AI가 짠 코드" 과제 10개 | 범위 선택에서 제외. 가드레일 미션 3이 맛보기 역할을 한다 |
| W-15 파편 페이지 IA 통합 | 범위 선택에서 제외 |
| A-08 강사 모드, A-09 멀티모델, A-10 평가 리포트 | P2, P3 항목 |
| W-04 코딩 표준 텍스트 정제 | 1차에서 LIGATURE 검사로 잡는 선까지. 전수 교정은 별건 |
| KO/EN 동시 갱신 (A-06 체크리스트) | 가드레일 연습장은 현재 한국어만. 영문화는 W-09 파이프라인과 함께 |

---

# 3차: 남은 백로그 (2026-09-13)

2차에서 범위 밖으로 미뤄 둔 것 중 세 가지를 처리했다.
W-05(코딩 표준 분할)와 CSP `unsafe-inline` 제거는 회귀 위험이 커서 이번에도 남겼다.

## 19. 코딩 표준 텍스트 정제 (W-04)

PDF 에서 텍스트를 뽑을 때 합자가 다른 글자로 바뀐다.
이 저장소에서는 세 가지 방식으로 깨져 있었다.

| 원래 | 깨진 모양 | 예 |
|:--|:--|:--|
| fi | 9 | `de9ned`, `identi9er`, `speci9ed` |
| fi | % | `unde%ned`, `unspeci%ed`, `quali%ed` |
| fl | 8 | (해당 없음) |

**기계적으로 치환하면 안 된다.** 같은 모양이 정상적인 코드에도 나온다.

```c
uint8_t u8a = 1.0f;      /* MISRA 예제의 변수 이름 */
0x9e3779b9               /* 16진 상수 */
```

그래서 `_gen/fix_ligatures.py` 는 **복원한 결과가 이 저장소 안에서
정상 표기로도 쓰일 때만** 바꾼다. 판단 근거를 코퍼스 자신에게서 가져오는 방식이다.

- 복원 14종, 108곳 수정. 예: `de9ned` → `defined` (정상 표기가 이미 256회 존재)
- 건드리지 않은 7종: `u8a`, `s8a`, `x9e3779b`, `K8s` 등. 복원해도 쓰이지 않는 말이라 코드로 판단
- `<pre>`, `<code>` 안은 아예 건드리지 않는다. 코드 블록 1,935개가 바이트 단위로 동일함을 확인

쪼개진 단어(`pointe r`, `fi elds`, `T rigraphs`)는 자동 탐지 결과를 한 건씩 확인해
27종 목록으로 확정했다. 붙이면 오히려 틀리는 것들은 **일부러 뺐다.**

| 뺀 것 | 이유 |
|:--|:--|
| `size of` | "the size of a structure". 띄어 쓰는 것이 맞다 |
| `can not`, `wake up`, `any way`, `name space` | 정상 영어 표현 |
| `prepared statement` | 영어로는 띄어 쓴다. 코드의 `PreparedStatement` 와 별개 |
| `pseudo random`, `non existent`, `multi threaded` | 표기 취향이지 결함이 아니다 |

`validate_build.py` 에 LIGATURE-SYMBOL 검사를 더했다. 같은 방식으로 자기 검증한다.
일부러 `unde%ned` 를 넣고 돌려 검사가 잡는지 확인했다.

## 20. AI가 만든 코드 과제 10개 (Track D)

`public/js/academy-data-ai.js`. 스키마는 기존 `ACADEMY_DATA.PRACTICAL` 과 같아서
CWE, KISA 49개 보안약점 매핑이 그대로 이어진다. `tags: ['ai-generated']` 로 구분한다.

| id | CWE | 무엇을 시켰더니 나온 코드인가 |
|:--|:--|:--|
| AID-01 | CWE-89 | "사용자 이름으로 주문 내역을 찾는 함수 만들어줘" |
| AID-02 | CWE-330 | "비밀번호 재설정 토큰 생성해주는 코드" |
| AID-03 | CWE-532 | "로그인 실패 원인을 알 수 있게 로그 좀 자세히 남겨줘" |
| AID-04 | CWE-798 | "결제 API 클라이언트. 바로 돌아가게 해줘" |
| AID-05 | CWE-22 | "첨부파일 내려받는 엔드포인트 구현해줘" |
| AID-06 | CWE-285 | "관리자만 쓸 수 있는 사용자 삭제 API 만들어줘" |
| AID-07 | CWE-502 | "세션 데이터를 파일로 저장했다가 다시 불러오는 코드" |
| AID-08 | CWE-295 | "SSL 인증서 오류가 나. 에러 안 나게 해줘" |
| AID-09 | CWE-327 | "회원가입할 때 비밀번호 저장하는 코드 만들어줘" |
| AID-10 | CWE-390 | "결제 처리 중에 예외 나도 서비스가 안 죽게 해줘" |

요청 문장(`aiPrompt`)을 화면에 함께 띄운다. "에러 안 나게 해줘" 같은 한 줄이
어떤 코드를 불러오는지 학습자가 직접 보게 하려는 것이다.

- `code-fix-lab.html` 에 출처 필터 추가: 전체 / AI가 만든 코드 / 기존 커리큘럼
- `code-review-game.html` 에서도 10개 전부 취약 라인이 도출된다
- 자체 검사: 모범 답안 10개 전부 채점 통과, 주석만 붙인 취약 코드 10개 전부 차단

## 21. AI 트랙 영문화 (W-09)

| 파일 | 방식 |
|:--|:--|
| `js/guardrail-missions.js` | 화면 문구를 `[한국어, English]` 쌍으로. `T()` 가 고른다 |
| `js/ai-track.js` | 모듈 라벨, 설명, 카드 제목, 선수 개념 라벨 |
| `ai-hub.html`, `ai-guardrail-lab.html` | 사이트 공통 `data-en` 방식, 언어 전환 버튼 |
| `js/registry.js` | 커버리지 배지와 미수록 목록 |

채점 규칙은 **두 언어를 모두 인정한다.** 한국어로 쓰든 영어로 쓰든 같은 기준이다.
교차 검증으로 확인했다.

| 검증 | 결과 |
|:--|:--|
| 한국어 UI, 한국어 모범답안 | 5개 전부 통과 |
| 영어 UI, 영어 모범답안 | 5개 전부 통과 |
| 한국어 UI, 영어 답안 | 5개 전부 통과 |
| 영어 UI, 한국어 답안 | 5개 전부 통과 |

영문화 과정에서 정규식 결함 세 건을 찾아 고쳤다.
`\b(rotat|separat|validat)\b` 처럼 어간 뒤에 단어 경계를 두면
"rotate", "separate" 같은 활용형이 잡히지 않는다.

## 22. 3차 검증 결과

```
python _gen/validate_build.py        -> 통과 (407개 파일, 검사 9종)
```

| 항목 | 결과 |
|:--|:--|
| 코드 블록 1,935개 바이트 동일 (합자 수정 후) | 동일 |
| LIGATURE-SYMBOL 검사 자체 시험 | 주입한 깨진 단어 3종 모두 검출 |
| AI 과제 10개 모범답안 채점 | 전부 통과 |
| AI 과제 10개 위장 제출(주석만 추가) | 전부 차단 |
| 코드 수정 실습 출처 필터 | AI 10개 / 기존 73개로 정확히 분리 |
| 가드레일 미션 KO, EN 왕복 채점 | 4가지 조합 전부 통과 |
| AI 허브, 연습장, 개념 카드 KO, EN 렌더 | 콘솔 오류 0 |
| 언어 전환 버튼 | 허브와 연습장 모두 즉시 반영 |

## 23. 3차에서도 남긴 것

| 항목 | 이유 |
|:--|:--|
| W-05 `coding-standards.html` 분할 | 3.2MB 단일 페이지. 트리 탐색, 앵커, 검색을 다시 설계해야 하고 회귀 범위가 넓다 |
| CSP `unsafe-inline` 제거 | 인라인 이벤트 3,549개를 405개 페이지에서 위임 방식으로 옮겨야 한다. 단계를 나눠 진행할 일 |
| W-15 파편 페이지 IA 통합 | 범위 선택에서 제외 |
| A-08 강사 모드, A-09 멀티모델, A-10 평가 리포트 | P2, P3 항목 |
| 13_ai-* 개념 카드 본문 영문화 | 카드 26개의 본문 전체 번역은 별건. 이번에는 학습 경로 메타데이터까지 |
