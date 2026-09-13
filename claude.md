# CLAUDE.md

이 문서는 WEB-VULN-SIM 보안 학습 포털을 유지보수할 때 따라야 할 프로젝트 기준이다.

> QA N-09 대응. 이 자리에는 원래 전혀 다른 프로젝트(한국투자증권 API 기반 자동매매봇)의
> 문서가 들어 있었다. AI 도구가 잘못된 컨텍스트를 물고 작업하게 만들므로 교체했다.

---

## 1. 프로젝트 정체성

웹, 인프라, 시큐어코딩 보안 취약점을 브라우저 안에서 체험하고 방어 방법을 익히는
**교육용 정적 웹 포털**이다. Firebase Hosting 으로 배포한다.

- 공격 시연은 전부 페이지 내부 mock 이다. 실제 외부 시스템을 공격하지 않는다.
- 학습 진도는 기본적으로 `localStorage` 에 남고, Google 로그인 시 Firestore 로 동기화한다.
- 콘텐츠는 KISA, 행정안전부, 금융보안원 공개 가이드라인을 개념적으로 재구성한 것이다.

핵심 전제 두 가지.

> 이 사이트는 "공격을 가르치는 곳"이 아니라 "왜 막아야 하는지 이해시키는 곳"이다.
> 시연을 추가할 때는 항상 방어 코드와 짝을 이루게 한다.

> 학습자가 콘솔을 열어 규칙을 우회할 수 있는 구조를 만들지 않는다.
> 수료 판정처럼 의미가 있는 판단은 서버가 한다.

---

## 2. 디렉터리 구조

```text
public/                     배포 루트 (Firebase Hosting)
  index.html                학습 트랙 4개로 가는 허브
  vuln-hub.html             취약점 학습 허브 (Track 01)
  secure-dev-portal.html    진단원 학습 포털 (Track 02)
  training-dashboard.html   실전 훈련장 (Track 03)
  coding-standards.html     C/C++ 코딩 표준 레퍼런스 (Track 04, 3.2MB)
  03_code_*.html            시큐어코딩 49개 보안약점 해설 (50종)
  04_design-sd*.html        설계 단계 보안 (20종)
  05_linux-u*.html          Linux 서버 점검 (41종)
  06_db-d*.html             DBMS 점검 (21종)
  07_fin-*.html             전자금융기반시설 점검 (43종)
  08_win-w*.html            Windows 서버 점검 (28종)
  09_net-n*.html            네트워크 장비 점검 (21종)
  10_sec-s*.html            보안장비 점검 (23종)
  11_cloud-c*.html          클라우드, 컨테이너 (20종)
  12_ics-ics*.html          제어시스템 ICS/SCADA (14종)
  13_ai-ai*.html            AI 보안 (26종)
  sim-*.html                인터랙티브 공격 시뮬레이터 (62종)
  privacy.html terms.html   개인정보 처리방침, 이용약관
  ai-hub.html               AI 보안 트랙 허브 (Track 05)
  ai-guardrail-lab.html     AI 가드레일 연습장 (미션 5개, 규칙 기반 채점)
  data/
    content-registry.json   콘텐츠 수치 단일 원천 (생성물)
  js/
    shell.js                공통 셸: 랜드마크, 푸터, 언어, 이전-다음
    boot-guard.js           window.onload 부팅 보호와 오류 표시
    registry.js             레지스트리 수치를 배지에 채움
    safety-notice.js        공격형 실습 진입 시 안전 고지
    ai-demo.js              키 없이 도는 데모 튜터 엔진
    ai-track.js             AI 트랙 학습 경로 데이터
    ai-card.js              AI 카드 상단 정보 띠와 이전-다음
    guardrail-missions.js   가드레일 미션과 루브릭 채점기 (KO/EN)
    academy-data-ai.js      AI 생성 코드 과제 10개 (tags: ai-generated)
    pwa.js  sw.js           PWA 설치와 오프라인
    progress.js             학습 진도 기록
    academy-data*.js        학습 콘텐츠 데이터 (합계 620KB)
    qbank/                  문제은행
    page-order.json         학습 페이지 순서 카탈로그
  icons/                    PWA 아이콘 (192, 512, maskable)

functions/index.js          수료증 발급과 검증, 데이터 삭제, AI 프록시
firestore.rules             Firestore 보안 규칙
firebase.json               보안 헤더, CSP, 리다이렉트, 캐시 정책
_gen/                       생성기와 주입 스크립트, 검증 게이트
```

---

## 3. 절대 원칙

### 생성기 산출물은 반드시 검증한다

이 저장소에서 나온 심각한 결함 대부분은 "생성기가 만든 결과를 아무도 검사하지 않는다"는
한 가지 원인에서 나왔다. 실제 사례.

- `inject_progress.py` 가 파일의 **첫 번째** `</body>` 를 치환했다. 시뮬레이터들은
  자바스크립트 문자열 안에 mock HTML 을 들고 있어서, 첫 `</body>` 가 문자열 내부였다.
  결과적으로 `<script>` 블록 한가운데에 `</script>` 가 박혀 **페이지 6개가 죽었다.**
  화면에는 자바스크립트 소스가 본문 텍스트로 20KB씩 노출됐다.

그래서 다음을 강제한다.

- 문서 끝을 찾을 때는 **반드시 `rfind('</body>')`** 를 쓴다. 정규식 `sub(..., count=1)` 금지.
- 자바스크립트 문자열 안에 HTML 을 담을 때 `</script>` 는 `<\/script>` 로 이스케이프한다.
- 파일을 건드리는 스크립트를 만들었으면 `_gen/validate_build.py` 에 검사도 함께 추가한다.
- 배포 전 `python _gen/validate_build.py` 가 통과해야 한다.

### 전역에 브라우저 내장 이름을 쓰지 않는다

`window.history`, `window.location`, `window.name`, `window.top` 등은
Window 의 설정 불가 접근자다. 최상위에서 `var history = []` 를 써도
선언이 **조용히 무시되고**, 첫 `history.push()` 에서 TypeError 로 페이지가 죽는다.

실제로 `sim-dast.html` 과 `ai-tutor.html` 두 곳에서 같은 원인으로 기능이 죽어 있었다.
대화 기록은 `chatLog`, 요청 기록은 `reqHistory` 처럼 이름을 바꾼다.

### 화면 수치는 레지스트리에서 읽는다

`public/data/content-registry.json` 이 콘텐츠 수치의 단일 원천이다.

- 생성: `python _gen/gen_registry.py`
- 표기: `<span data-wvs-count="totals.interactiveTotal">367</span>`
  (HTML 안의 값은 스크립트 실패 시 보일 대비값이다)
- 커버리지: `data-wvs-coverage="linux"`, 미수록 목록: `data-wvs-missing="linux"`
- `validate_build.py` 가 대비값과 레지스트리가 어긋나면 배포를 막는다

콘텐츠를 추가하거나 지웠으면 `gen_registry.py` 를 다시 돌린다.
없는 항목은 "완전 구성" 이라고 쓰지 말고 커버리지로 드러낸다.

### 신뢰 경계를 클라이언트에 두지 않는다

- 수료 판정, 수료번호 발급, 서명은 Cloud Functions 에서만 한다.
- 브라우저가 보낸 진도 수치, 완료 개수, 점수를 그대로 믿지 않는다.
- `window.force*`, `*ForDev` 같은 전역 우회 함수를 배포본에 남기지 않는다.
  실제로 `forceUnlockForDev()` 한 줄로 수료증이 발급되던 적이 있다.
- 서명에는 서버만 아는 키를 쓴다. 비밀 키 없는 SHA-256 은 위조 방지가 되지 않는다.

### 개인정보는 필요한 만큼만 다룬다

- 수료증 조회 응답에는 마스킹된 이름만 담는다.
- Firestore 규칙의 기본값은 거부다. 새 컬렉션을 만들면 규칙도 같이 쓴다.
- 수집 항목을 늘리면 `public/privacy.html` 을 같은 커밋에서 갱신한다.

### 외부 의존은 검증 가능한 형태로만 둔다

- 외부 스크립트와 스타일에는 `integrity` 와 `crossorigin` 을 붙인다.
- 해시는 npm 배포본에서 계산하고, 그 패키지를 그대로 서빙하는 CDN 경로를 쓴다
  (jsDelivr `/npm/...`). 재포장하는 CDN 경로는 해시 일치를 보증하지 않는다.
- `cdn.tailwindcss.com` 같은 런타임 컴파일 CDN 은 쓰지 않는다. SRI 를 걸 수 없고
  CSP 에서 `unsafe-eval` 을 요구한다.

### 접근성은 기능이다

- 이동은 `<a>`, 상태 변경은 `<button>` 으로 만든다.
  `<div onclick>` 은 키보드 사용자에게 존재하지 않는 버튼이다.
- 새 페이지에는 skip link 와 `js/shell.js` 가 들어가야 한다
  (`python _gen/inject_shell.py` 가 멱등으로 처리한다).
- 상태 변화는 `aria-live` 또는 `role="alert"` 로 알린다.

---

## 4. 자주 하는 작업

```bash
# 공통 셸 주입 (skip link, 랜드마크, 푸터, 이전-다음)
python _gen/inject_shell.py

# 콘텐츠 레지스트리 재생성 (콘텐츠를 더하거나 지웠으면 필수)
python _gen/gen_registry.py

# 안전 고지 주입 (공격형 실습 페이지)
python _gen/inject_safety.py

# AI 트랙 학습 경로 주입 (13_ai-* 카드)
python _gen/inject_ai_meta.py

# PDF 합자 깨짐 복원 (먼저 --dry 로 무엇을 고칠지 확인한다)
python _gen/fix_ligatures.py --dry
python _gen/fix_ligatures.py

# 진도 엔진 주입
python _gen/inject_progress.py

# sitemap 재생성
python _gen/gen_sitemap.py

# 배포 전 검증 (통과해야 배포)
python _gen/validate_build.py

# 로컬 확인
python -m http.server 8099 --directory public

# 배포
firebase deploy --only hosting
firebase deploy --only functions
firebase deploy --only firestore:rules
```

---

## 5. Cloud Functions 배포 준비

```bash
# 수료증 서명 키 (한 번만 생성, 분실하면 기존 수료증 검증 불가)
openssl rand -hex 32
firebase functions:secrets:set CERT_SIGNING_KEY

# AI 튜터 프록시를 쓸 경우
firebase functions:secrets:set ANTHROPIC_API_KEY
```

`functions/index.js` 의 `ALLOW_AI_PROXY` 는 기본이 `false` 다.
조직 키로 과금되므로 사용량 정책(`DAILY_MESSAGE_LIMIT`)을 정한 뒤 켠다.

---

## 6. 콘텐츠 작성 규칙

- 공격 시연에는 반드시 방어 코드와 "쉽게 말하면" 비유 설명을 함께 둔다.
- 화면에 수치를 쓸 때는 데이터에서 센 값을 쓴다. 손으로 적은 값은 금방 어긋난다.
  (실제로 "규칙 500여종" 표기에 실제 1,117개, "319개+ 실습"에 실제 369개였다.)
- PDF 에서 추출한 텍스트는 두 가지로 깨진다. 단어 안에 공백이 들어가거나
  (`defi ne`, `pointe r`), 합자가 다른 글자로 바뀐다 (`de9ned`, `unde%ned`).
  `validate_build.py` 의 LIGATURE, LIGATURE-SYMBOL 검사가 잡고,
  `_gen/fix_ligatures.py` 가 고친다.
- 합자 복원을 정규식으로 일괄 치환하지 않는다. `uint8_t u8a`, `0x9e3779b9` 처럼
  정상 코드가 같은 모양이다. 복원 결과가 저장소 안에서 정상 표기로도 쓰일 때만 바꾼다.
- 쪼개진 단어를 붙일 때도 마찬가지다. `size of`, `can not`, `prepared statement` 는
  띄어 쓰는 것이 맞다. 확인한 목록만 `fix_ligatures.py` 의 `SPLITS` 에 넣는다.
- 제작 공정 설명("PDF 원문에서 분리되지 않아...")을 학습자 화면에 노출하지 않는다.
- 실존 상표를 모의 화면 소품으로 쓰지 않는다. 가상 브랜드를 만든다.

---

## 7. 파일명과 URL 규칙

- 학습 페이지는 `<번호>_<도메인>-<식별자>.html` 또는 `sim-<식별자>.html`.
- 구분자는 하이픈으로 통일한다. 밑줄을 쓰면 주입 스크립트가 걸러내지 못한다
  (`sim_insufficient_session.html` 이 그 사례였다).
- URL 오타를 발견하면 정규 URL 을 만들고 `firebase.json` 의 `redirects` 에 301 을 추가한다.
  파일명만 바꾸면 외부 링크와 검색 색인이 깨진다.

---

## 8. 변경 시 확인해야 하는 것

| 바꾼 것 | 같이 봐야 하는 것 |
|:--|:--|
| 새 페이지 추가 | `inject_shell.py`, `gen_sitemap.py`, `page-order.json` |
| 파일명 변경 | 내부 링크 전수, sitemap, `firebase.json` 리다이렉트 |
| 외부 라이브러리 추가 | SRI 해시, `firebase.json` 의 CSP, `privacy.html` 의 위탁 표 |
| 수집 데이터 추가 | `firestore.rules`, `privacy.html`, 삭제 경로 |
| 인라인 이벤트 추가 | CSP `script-src` 강화 계획과 충돌 여부 |
| 콘텐츠 수 변경 | `python _gen/gen_registry.py` 재실행, `gen_sitemap.py`, `page-order.json` |
| 공격형 실습 추가 | `_gen/inject_safety.py` 재실행 |
| AI 개념 카드 추가 | `js/ai-track.js` 의 경로 표, `_gen/inject_ai_meta.py` 재실행 |
| AI 진도 키 추가 | `wvs_ai_*` 네임스페이스를 쓴다 |
| 실습 과제 추가 | `codefix-grader.js` 로 자체 채점 시험 (모범답안 통과, 위장 제출 차단) |
| 화면 문구 추가 | 한국어와 영어를 같이 쓴다. 채점 규칙도 두 언어를 인정해야 한다 |

---

## 9. 채점 규칙을 쓸 때

- 어간으로 대안을 적었으면 뒤에 `\b` 를 두지 않는다.
  `/\b(rotat|separat)\b/` 는 "rotate", "separate" 를 잡지 못한다.
- 새 과제나 미션을 만들면 **모범 답안이 자기 루브릭을 통과하는지** 반드시 확인한다.
  실제로 처음 작성한 미션 5개 중 2개가 자기 기준에 미달했다.
- 빈 답안이 "하지 않았다" 류 항목(부정형 기준)을 거저 통과하지 않게 막는다.

---

## 10. 알려진 미해결 과제

- 인라인 이벤트 핸들러가 약 3,500개라 `script-src` 에서 `unsafe-inline` 을 아직 못 뺐다.
  `firebase.json` 에 보고 전용 CSP 를 함께 배포해 두었으니, 위반 로그를 보며
  생성기 레벨에서 이벤트 위임 방식으로 전환한 뒤 조인다.
- `coding-standards.html` 이 3.2MB 단일 페이지이고 버튼이 2,700개가 넘는다.
  표준별, 섹션별 분할과 지연 로드가 필요하다.
- 수료증 서버 발급으로 전환했으므로, 기존 자가검증 링크(`?d=&h=`)는
  이행 기간이 끝나면 제거한다.
