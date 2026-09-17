/**
 * 접근성 정적 회귀 검사 (QA-P1-06 / QA-P2-03)
 *
 * QA 감사가 axe 로 재현한 것들 중 "정적으로 확정 가능한" 것만 검사한다.
 * 브라우저 없이 CSS 선언과 HTML 구조만 보므로, 여기서 통과했다고 접근성이
 * 검증된 것은 아니다. 회귀를 막는 최소선이다.
 *
 *   1) 색 대비 — 같은 규칙에서 color 와 background 를 함께 선언한 경우만.
 *      (상속된 배경은 정적으로 알 수 없어 판단하지 않는다. 모른다고 통과 처리하지 말 것.)
 *   2) 폼 컨트롤 접근 가능한 이름 — label/aria-label/aria-labelledby/title/placeholder 중 없음
 *   3) 문서 구조 — <main> 랜드마크, <h1>
 *   4) 보이는 포커스 — outline:none 을 :focus 에 걸고 대체 표시가 없는 규칙
 *
 * 실행: node tools/test-a11y.js [--list]   (--list 는 위반을 전부 출력)
 */
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const PUB = path.join(ROOT, 'public');
const LIST = process.argv.includes('--list');

/* ── 색 계산 ───────────────────────────────────────────── */
const NAMED = { white: '#ffffff', black: '#000000', red: '#ff0000', transparent: null };
function parseColor(raw) {
  if (!raw) return null;
  const v = raw.trim().toLowerCase();
  if (v in NAMED) return NAMED[v];
  let m = v.match(/^#([0-9a-f]{3})$/);
  if (m) return '#' + m[1].split('').map((c) => c + c).join('');
  m = v.match(/^#([0-9a-f]{6})$/);
  if (m) return '#' + m[1];
  m = v.match(/^rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)\s*(?:[,/]\s*([\d.]+))?\s*\)$/);
  if (m) {
    if (m[4] !== undefined && parseFloat(m[4]) < 0.95) return null;   // 반투명은 판단 불가
    return '#' + [m[1], m[2], m[3]].map((x) => ('0' + Number(x).toString(16)).slice(-2)).join('');
  }
  return null;                                                        // var()/그라디언트/키워드 → 판단 안 함
}
function luminance(hex) {
  const c = hex.slice(1).match(/../g).map((h) => parseInt(h, 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}
function contrast(fg, bg) {
  const a = luminance(fg), b = luminance(bg);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}

/* ── CSS 수집 ─────────────────────────────────────────── */
function cssBlocks(text) {
  /* 아주 단순한 룰 분해. @media 안의 규칙도 같은 방식으로 잡힌다(셀렉터만 어긋남). */
  const out = [];
  const re = /([^{}@]+)\{([^{}]*)\}/g;
  let m;
  while ((m = re.exec(text))) out.push({ sel: m[1].trim().replace(/\s+/g, ' '), body: m[2] });
  return out;
}
function decl(body, prop) {
  const re = new RegExp('(?:^|;)\\s*' + prop + '\\s*:\\s*([^;!]+)', 'i');
  const m = body.match(re);
  return m ? m[1].trim() : null;
}
function fontPx(body) {
  const fs_ = decl(body, 'font-size') || (decl(body, 'font') || '').match(/(\d*\.?\d+)(px|rem|em)/)?.[0];
  if (!fs_) return null;
  const m = String(fs_).match(/(\d*\.?\d+)\s*(px|rem|em)/);
  if (!m) return null;
  const n = parseFloat(m[1]);
  return m[2] === 'px' ? n : n * 16;
}
function isBold(body) {
  const w = decl(body, 'font-weight') || '';
  return /bold|[7-9]00/.test(w);
}

let pass = 0;
const fails = [];
function check(name, fn) {
  let d;
  try { d = fn(); } catch (e) { d = e.message; }
  if (d === true || d === undefined) { pass++; console.log('  PASS  ' + name); }
  else { fails.push(name + ' — ' + d); console.log('  FAIL  ' + name + ' — ' + d); }
}

const htmlFiles = fs.readdirSync(PUB).filter((f) => f.endsWith('.html'));
const cssFiles = fs.existsSync(path.join(PUB, 'css'))
  ? fs.readdirSync(path.join(PUB, 'css')).filter((f) => f.endsWith('.css')).map((f) => 'css/' + f)
  : [];

/* 검사에서 빼는 곳 — 이유를 적는다. */
const CONTRAST_EXEMPT = [
  /::(before|after)/,          // 장식용 의사요소
  /\bplaceholder\b/,           // placeholder 는 본문 텍스트가 아니다(레이블로 대체 요구)
];

console.log('\n[1] 색 대비 (같은 규칙에 color + background 를 함께 선언한 경우)');

const contrastHits = [];
function scanContrast(label, text) {
  for (const b of cssBlocks(text)) {
    if (CONTRAST_EXEMPT.some((re) => re.test(b.sel))) continue;
    const fg = parseColor(decl(b.body, 'color'));
    const bgRaw = decl(b.body, 'background-color') || decl(b.body, 'background');
    if (!fg || !bgRaw) continue;
    const bgFirst = String(bgRaw).split(/\s+/)[0];
    const bg = parseColor(bgFirst);
    if (!bg) continue;                                    // 그라디언트/변수 → 판단 안 함
    const px = fontPx(b.body);
    const large = px !== null && (px >= 24 || (px >= 18.66 && isBold(b.body)));
    const need = large ? 3.0 : 4.5;
    const r = contrast(fg, bg);
    if (r < need) contrastHits.push({ where: label, sel: b.sel.slice(0, 70), fg, bg, r: r.toFixed(2), need });
  }
}
for (const f of cssFiles) scanContrast(f, fs.readFileSync(path.join(PUB, f), 'utf8'));
for (const f of htmlFiles) {
  const html = fs.readFileSync(path.join(PUB, f), 'utf8');
  const styles = html.match(/<style[^>]*>([\s\S]*?)<\/style>/gi) || [];
  for (const s of styles) scanContrast(f, s.replace(/<\/?style[^>]*>/gi, ''));
}
check('명시적으로 선언된 전경/배경 조합이 WCAG AA 를 만족한다', () => {
  if (!contrastHits.length) return true;
  const byFile = {};
  contrastHits.forEach((h) => { byFile[h.where] = (byFile[h.where] || 0) + 1; });
  const top = Object.entries(byFile).sort((a, b) => b[1] - a[1]).slice(0, 6)
    .map(([k, v]) => k + '(' + v + ')').join(', ');
  if (LIST) contrastHits.forEach((h) => console.log('        ' + h.where + ' | ' + h.sel + ' | ' + h.fg + ' on ' + h.bg + ' = ' + h.r + ' < ' + h.need));
  return contrastHits.length + '건 — ' + top;
});

console.log('\n[2] 폼 컨트롤 접근 가능한 이름');

/* \b 로 끊으면 JS 코드 `input.length` 나 `input[i]` 까지 태그로 오인한다.
   태그 이름 뒤에는 공백·/·> 중 하나가 와야 한다. */
const CONTROL_RE = /<(input|select|textarea)(?=[\s/>])([^>]*)>/gi;
/* 코드 예시가 JS 문자열 안에 들어가면 따옴표가 \" 로 이스케이프된다. 그것도 읽는다. */
const TYPE_RE = /\\?\btype\s*=\s*\\?["']([^"'\\]*)/i;
const nameless = [];
for (const f of htmlFiles) {
  const html = fs.readFileSync(path.join(PUB, f), 'utf8');
  /* for= 로 연결된 id 와 <label> 로 감싼 경우를 모두 수집 */
  const labelFor = new Set((html.match(/<label[^>]*\bfor\s*=\s*["']([^"']+)["']/gi) || [])
    .map((s) => (s.match(/for\s*=\s*["']([^"']+)["']/i) || [])[1]));
  const wrapped = new Set();
  const wrapRe = /<label\b[^>]*>([\s\S]*?)<\/label>/gi;
  let w;
  while ((w = wrapRe.exec(html))) {
    const ids = w[1].match(/\bid\s*=\s*["']([^"']+)["']/gi) || [];
    ids.forEach((s) => wrapped.add((s.match(/["']([^"']+)["']/) || [])[1]));
    if (/<(input|select|textarea)\b/i.test(w[1])) wrapped.add('__anon__' + w.index);
  }
  CONTROL_RE.lastIndex = 0;
  let m;
  while ((m = CONTROL_RE.exec(html))) {
    const attrs = m[2] || '';
    const type = (attrs.match(TYPE_RE) || [])[1] || 'text';
    if (/^(hidden|submit|reset|button|image)$/i.test(type)) continue;
    if (/\b(aria-label|aria-labelledby|title)\s*=/.test(attrs)) continue;
    /* \" 가 섞인 태그는 JS 문자열 안에 들어 있는 코드 예시다. 화면의 폼이 아니다. */
    if (attrs.includes('\\"') || attrs.includes("\\'")) continue;
    const id = (attrs.match(/\bid\s*=\s*["']([^"']+)["']/i) || [])[1];
    if (id && (labelFor.has(id) || wrapped.has(id))) continue;
    /* <label>…<input>…</label> 형태(감싸기)인지 위치로 확인 */
    const before = html.lastIndexOf('<label', m.index);
    const closed = html.lastIndexOf('</label>', m.index);
    if (before > closed) continue;
    nameless.push(f + ': ' + (LIST ? JSON.stringify(m[0].slice(0, 150)) : '<' + m[1].toLowerCase() + (id ? ' id=' + id : '') + '>'));
  }
}
check('input/select/textarea 에 접근 가능한 이름이 있다', () => {
  if (!nameless.length) return true;
  if (LIST) nameless.forEach((s) => console.log('        ' + s));
  const files = [...new Set(nameless.map((s) => s.split(':')[0]))];
  return nameless.length + '건 / ' + files.length + '개 파일 — ' + files.slice(0, 6).join(', ');
});

console.log('\n[3] 문서 구조');

/* 본문 랜드마크는 두 경로 중 하나로 보장된다.
     (a) 페이지가 직접 <main> 또는 role="main" 을 쓴다
     (b) 공용 크롬(soc-chrome.js)이 h1 을 담은 블록에 런타임으로 role="main" 을 붙인다
   519개 페이지의 서로 다른 레이아웃을 일괄 수정하는 것보다 (b)가 깨질 위험이 작다.
   그래서 여기서는 "둘 중 하나가 보장되는가"를 본다 — h1 이 없으면 (b)도 못 한다. */
/* 이 사이트는 자바스크립트 문자열 안에 모의 HTML 을 잔뜩 들고 있다(공격 시연용).
   원본을 그대로 정규식으로 보면 그 문자열 속 <h1> 까지 '있다'고 세어 버린다.
   실제로 sim-dast.html 이 그 경우였다 — 소스에 <h1> 이 2개 있지만 둘 다
   모의 쇼핑몰 응답을 만드는 JS 문자열 안이라, 렌더된 페이지에는 제목이 없었는데도
   이 검사는 계속 통과했다. 그래서 <script> 블록을 걷어낸 뒤에 판정한다. */
function markupOnly(s) {
  let out = '', pos = 0;
  for (;;) {
    const m = /<script\b[^>]*>/i.exec(s.slice(pos));
    if (!m) { out += s.slice(pos); break; }
    // 여는 태그는 남긴다 — src="/js/soc-chrome.js" 를 아래에서 확인해야 하므로
    // 태그까지 지우면 '공용 크롬 없음'으로 잘못 판정된다.
    out += s.slice(pos, pos + m.index) + m[0];
    const end = s.indexOf('</script>', pos + m.index + m[0].length);
    if (end < 0) break;
    pos = end + 9;
  }
  return out;
}
const noMain = htmlFiles.filter((f) => {
  const s = markupOnly(fs.readFileSync(path.join(PUB, f), 'utf8'));
  if (/<main[\s>]/i.test(s) || /role\s*=\s*["']main["']/i.test(s)) return false;
  return !(/soc-chrome\.js/.test(s) && /<h1[\s>]/i.test(s));
});
const noH1 = htmlFiles.filter((f) => !/<h1[\s>]/i.test(markupOnly(fs.readFileSync(path.join(PUB, f), 'utf8'))));
check('모든 페이지에 본문 랜드마크가 보장된다 (<main>/role=main 또는 공용 크롬 + h1)', () => noMain.length === 0
  || noMain.length + '개 — ' + noMain.slice(0, 5).join(', '));
check('모든 페이지에 <h1> 이 있다', () => noH1.length === 0
  || noH1.length + '개 — ' + noH1.slice(0, 5).join(', '));
check('공용 크롬이 본문 랜드마크와 건너뛰기 링크를 실제로 붙인다', () => {
  const s = fs.readFileSync(path.join(PUB, 'js', 'soc-chrome.js'), 'utf8');
  return (/setAttribute\('role', 'main'\)/.test(s) && /wvsx-skip/.test(s))
    || 'soc-chrome.js 에 markMainLandmark/addSkipLink 구현이 없다';
});

console.log('\n[4] 보이는 포커스');

const focusKill = [];
function scanFocus(label, text) {
  const blocks = cssBlocks(text);
  /* `:focus { outline:none }` + `:focus-visible { outline:… }` 는 요즘 권장되는 조합이다.
     마우스 클릭에는 링을 안 띄우고 키보드 이동에는 띄운다.
     같은 규칙 안만 보면 이 정상 패턴을 위반으로 잡으므로, 같은 셀렉터의
     :focus-visible 짝이 문서 안에 있는지도 함께 본다. */
  const visibleBases = new Set();
  let universalFocusVisible = false;      // 셀렉터가 그냥 `:focus-visible` 이면 모든 요소를 덮는다
  for (const b of blocks) {
    if (!/:focus-visible/.test(b.sel)) continue;
    const o = decl(b.body, 'outline');
    const hasIndicator = (o && !/^(none|0(px)?)$/i.test(o.trim()))
      || decl(b.body, 'box-shadow') || decl(b.body, 'border') || decl(b.body, 'border-color');
    if (!hasIndicator) continue;
    b.sel.split(',').forEach((one) => {
      const base = one.replace(/:focus-visible/g, '').trim();
      if (base === '' || base === '*') universalFocusVisible = true;
      else visibleBases.add(base);
    });
  }
  for (const b of blocks) {
    if (!/:focus(?!-visible)/.test(b.sel)) continue;
    const o = decl(b.body, 'outline');
    if (!o || !/^(none|0(px)?)$/i.test(o.trim())) continue;
    /* outline 을 껐다면 box-shadow/border 로 대체 표시가 있어야 한다 */
    if (decl(b.body, 'box-shadow') || decl(b.body, 'border') || decl(b.body, 'border-color')) continue;
    if (universalFocusVisible) continue;                           // 전역 :focus-visible 이 덮는다
    const bases = b.sel.split(',').map((one) => one.replace(/:focus\b/g, '').trim());
    if (bases.every((base) => visibleBases.has(base))) continue;   // 같은 셀렉터의 :focus-visible 짝이 있다
    focusKill.push(label + ' | ' + b.sel.slice(0, 60));
  }
}
for (const f of cssFiles) scanFocus(f, fs.readFileSync(path.join(PUB, f), 'utf8'));
for (const f of htmlFiles) {
  const html = fs.readFileSync(path.join(PUB, f), 'utf8');
  (html.match(/<style[^>]*>([\s\S]*?)<\/style>/gi) || [])
    .forEach((s) => scanFocus(f, s.replace(/<\/?style[^>]*>/gi, '')));
}
check(':focus 에서 outline 을 끄면 대체 표시가 있다', () => {
  if (!focusKill.length) return true;
  if (LIST) focusKill.forEach((s) => console.log('        ' + s));
  return focusKill.length + '건 — ' + focusKill.slice(0, 3).join(' / ');
});

check('공용 토큰에 전역 포커스 링이 정의돼 있다', () => {
  const css = fs.readFileSync(path.join(PUB, 'css', 'platform-tokens.css'), 'utf8');
  return /:focus-visible/.test(css) || 'platform-tokens.css 에 :focus-visible 규칙이 없다';
});

console.log('\n' + (fails.length
  ? 'FAILED ' + fails.length + ' / ' + (pass + fails.length) + (LIST ? '' : '\n  (--list 로 전체 위반 출력)')
  : 'ALL ' + pass + ' CHECKS PASSED') + '\n');
process.exit(fails.length ? 1 : 0);
