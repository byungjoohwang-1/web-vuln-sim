# 신규 시뮬레이터 제작 스펙 (WEB-VULN-SIM)

모든 신규 `sim-*.html`은 **자기완결 단일 HTML**(빌드 불필요, 외부 의존 최소)이며,
하나의 제품처럼 보이도록 아래 공통 규약을 **정확히** 따른다.
레퍼런스 구현: `public/sim-open-redirect.html` (이 파일을 복제·변형해서 만들 것).

## 0. 절대 원칙
- **교육용 시뮬레이션**이다. 실제 네트워크 공격/실제 호스트 접근을 절대 수행하지 않는다.
  모든 "공격"은 페이지 내부의 mock 대상(JS 함수)에 대해서만 동작한다.
- 실제 악성코드/실동작 익스플로잇 페이로드를 그대로 제공하지 않는다(개념·교육 수준).
- 한 화면 안에서 **취약 동작 → 공격 시연 → 방어(secure) 비교 → 원리 설명**이 모두 보이게 한다.

## 1. <head> 표준 블록 (그대로 사용, 제목/설명만 교체)
```html
<!DOCTYPE html>
<html lang="ko">
<head><meta name="theme-color" content="#0ea5e9"><link rel="manifest" href="/manifest.json"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{제목 KO} · WEB-VULN-SIM</title>
  <meta name="description" content="{한줄 설명}">
  <style>{공통 CSS 토큰 + 페이지 CSS}</style>
</head>
```

## 2. 공통 CSS 토큰 (SOC/pentest 콘솔 다크 테마 — 전 시뮬 통일)
```css
:root{
  --bg:#0b1220; --panel:#111a2e; --panel2:#0f172a; --border:#1e293b;
  --ink:#e2e8f0; --muted:#94a3b8; --accent:#38bdf8; --accent2:#818cf8;
  --bad:#ef4444; --bad-bg:#3b1418; --good:#22c55e; --good-bg:#0f2a18;
  --warn:#f59e0b; --mono:'JetBrains Mono','Consolas',monospace;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI','Malgun Gothic',sans-serif;background:var(--bg);color:var(--ink);line-height:1.55}
.wrap{max-width:1200px;margin:0 auto;padding:18px 16px 80px}
.topbar{display:flex;align-items:center;gap:14px;background:#0b1220;border-bottom:1px solid var(--border);padding:10px 16px;position:sticky;top:0;z-index:50}
.topbar a{color:#7dd3fc;text-decoration:none;font-size:13px;font-family:var(--mono)}
.topbar .sp{margin-left:auto}
.langbtn{cursor:pointer;border:1px solid #334155;background:#1e293b;color:#e2e8f0;border-radius:999px;padding:5px 12px;font-size:12.5px;font-weight:700;font-family:var(--mono)}
.hero{padding:18px 4px 8px}
.hero h1{font-size:23px;color:#fff;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.hero .sub{color:var(--muted);font-size:13.5px;margin-top:6px;max-width:820px}
.kisa{font-family:var(--mono);font-size:11px;font-weight:700;color:#0c4a6e;background:#7dd3fc;border-radius:6px;padding:2px 8px}
.card{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:16px 18px;margin:14px 0;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.card h2{font-size:15px;color:#7dd3fc;margin-bottom:10px;font-family:var(--mono)}
.row{display:flex;gap:14px;flex-wrap:wrap}.col{flex:1;min-width:280px}
label{display:block;font-size:12px;color:var(--muted);margin:8px 0 4px}
input,select,textarea{width:100%;background:var(--panel2);border:1px solid #334155;color:var(--ink);border-radius:8px;padding:9px 11px;font-family:var(--mono);font-size:13px}
textarea{min-height:90px;resize:vertical}
button.act{cursor:pointer;border:none;border-radius:8px;padding:10px 16px;font-weight:700;font-size:13px;font-family:var(--mono)}
button.run{background:var(--bad);color:#fff}button.fix{background:var(--good);color:#06210f}button.ghost{background:#1e293b;color:#cbd5e1;border:1px solid #334155}
pre,.out{background:#05080f;border:1px solid var(--border);border-radius:8px;padding:12px;font-family:var(--mono);font-size:12.5px;white-space:pre-wrap;word-break:break-word;overflow:auto;max-height:340px}
.vuln{border-left:4px solid var(--bad)}.secure{border-left:4px solid var(--good)}
.tag{display:inline-block;font-family:var(--mono);font-size:11px;font-weight:700;border-radius:6px;padding:2px 8px}
.tag.bad{background:var(--bad-bg);color:#fca5a5}.tag.good{background:var(--good-bg);color:#86efac}
.note{background:#0f172a;border-left:4px solid var(--accent);border-radius:8px;padding:11px 13px;font-size:13px;color:#cbd5e1;margin-top:10px}
.disc{margin-top:18px;font-size:12px;color:#64748b;border-top:1px dashed #334155;padding-top:10px}
body.lang-en .ko{display:none}body:not(.lang-en) .en{display:none}
table{width:100%;border-collapse:collapse;font-size:12.5px;font-family:var(--mono)}
th,td{border:1px solid var(--border);padding:6px 8px;text-align:left}th{background:#0f172a;color:#7dd3fc}
```

## 3. 표준 상단바 + 영웅 영역 (그대로)
```html
<div class="topbar">
  <a href="index.html">🏠 <span data-en="Home">홈</span></a>
  <a href="vuln-hub.html"><span data-en="Vuln Hub">취약점 학습 허브</span></a>
  <span class="sp"></span>
  <button class="langbtn" onclick="toggleLang()"><span data-en="한국어">English</span> ⇄</button>
</div>
<div class="wrap">
  <div class="hero">
    <h1>{이모지} <span data-en="{EN title}">{KO 제목}</span> <span class="kisa">KISA #{번호} · {약점명}</span></h1>
    <div class="sub" data-en="{EN subtitle}">{KO 한줄 설명}</div>
  </div>
  ... 시뮬 본문 ...
  <div class="disc" data-en="Educational simulation only. All attacks run against an in-page mock target; no real systems are accessed.">
    ⚠️ 교육용 시뮬레이션입니다. 모든 공격은 페이지 내부 mock 대상에 대해서만 동작하며 실제 시스템에 접근하지 않습니다.
  </div>
</div>
```

## 4. i18n (자기완결 — bilingual.js 의존 금지)
정적 텍스트는 `data-en` 속성(EN HTML)을, 동적 JS 출력은 `L(ko,en)`을 사용.
`wvs_lang` / `lang` localStorage 키 공유(다른 페이지와 연동). 아래 스크립트를 그대로 넣는다.
```html
<script>
function isEn(){try{return (localStorage.getItem('wvs_lang')||localStorage.getItem('lang'))==='en';}catch(e){return false;}}
function L(ko,en){return isEn()?en:ko;}
function applyLang(){
  var en=isEn();
  document.documentElement.lang=en?'en':'ko';
  document.querySelectorAll('[data-en]').forEach(function(el){
    if(el.getAttribute('data-ko')===null) el.setAttribute('data-ko', el.innerHTML);
    el.innerHTML = en ? el.getAttribute('data-en') : el.getAttribute('data-ko');
  });
  document.body.classList.toggle('lang-en', en);
  if(window.renderDynamic){try{window.renderDynamic();}catch(e){}}
}
function toggleLang(){try{var v=isEn()?'ko':'en';localStorage.setItem('wvs_lang',v);localStorage.setItem('lang',v);}catch(e){}applyLang();}
document.addEventListener('DOMContentLoaded', applyLang);
</script>
```
- 동적으로 텍스트를 그리는 패널은 함수 `renderDynamic()`로 묶어 두면 언어 전환 시 자동 재렌더된다.
- `data-en` 값에 따옴표가 필요하면 HTML 엔티티(`&quot;`) 사용.

## 5. 시뮬 본문 필수 구성요소
1. **취약 데모(card.vuln)**: 입력 → "취약 실행" 버튼 → mock 결과(`.out`)에 공격 성공 증거 표시.
2. **공격 프리셋**: 대표 공격 입력을 버튼으로 1클릭 주입(설명 포함).
3. **방어 비교(card.secure)**: 같은 입력을 "안전 구현"으로 실행 → 공격 차단되는 결과 표시.
4. **원리 설명(note)**: 왜 취약한지 / 공격 메커니즘 / 방어 핵심(검증·인코딩·최소권한 등). KO/EN.
5. **취약 vs 안전 코드 스니펫**(pre) 1쌍 이상 — 자체 작성, 언어는 약점에 맞게(C/Java/Python/JS).

## 6. 품질 기준
- 순수 vanilla JS. 외부 스크립트는 가급적 없음(필요 시 CDN 1개 이내, 버전 고정).
- JS 콘솔 에러 0. `new Function(scriptBody)`로 파싱되어야 함(문법 오류 금지).
- 모바일 반응형(이미 토큰의 flex-wrap으로 기본 대응).
- 분량 250~600줄, 실제 상용 학습 포털 수준의 밀도.
- 각 시뮬은 해당 약점의 **실제 메커니즘**을 정확히 반영(추측 금지).

## 7. 산출 후 vuln-hub 배선
신규 sim 파일명은 이 문서의 배정표를 따른다. 배선(허브 링크 추가)은 메인 작업자가 일괄 수행하므로
에이전트는 **sim 파일 생성에만 집중**한다.
