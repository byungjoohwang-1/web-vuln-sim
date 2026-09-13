/**
 * 색 대비 일괄 교정 (QA-P1-06).
 *
 * tools/test-a11y.js 가 찾아내는 "같은 규칙에서 color 와 background 를 함께 선언했는데
 * WCAG AA 에 못 미치는" 조합만 고친다. 규칙 단위로만 손대고, 다른 선언은 건드리지 않는다.
 *
 * 교정 방침 (브랜드 색을 최대한 보존하는 쪽):
 *   밝은 배경 + 흰 글자   → 글자를 어둡게 (#0b1220). 배경색을 그대로 두는 쪽이 디자인 손상이 적다.
 *   어두운 배경 + 흰 글자  → 배경을 기준 충족까지 조금 어둡게
 *   밝은 배경 + 어두운 글자 → 글자를 기준 충족까지 어둡게
 *   어두운 배경 + 밝은 글자 → 글자를 기준 충족까지 밝게
 *
 * 실행: node tools/fix-a11y-contrast.js [--dry]
 */
'use strict';
const fs = require('fs');
const path = require('path');

const PUB = path.join(__dirname, '..', 'public');
const DRY = process.argv.includes('--dry');

const NAMED = { white: '#ffffff', black: '#000000' };
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
    if (m[4] !== undefined && parseFloat(m[4]) < 0.95) return null;
    return '#' + [m[1], m[2], m[3]].map((x) => ('0' + Number(x).toString(16)).slice(-2)).join('');
  }
  return null;
}
function lum(hex) {
  const c = hex.slice(1).match(/../g).map((h) => parseInt(h, 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}
function ratio(a, b) {
  const l1 = lum(a), l2 = lum(b);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}
function toHex(r, g, b) {
  return '#' + [r, g, b].map((x) => ('0' + Math.max(0, Math.min(255, Math.round(x))).toString(16)).slice(-2)).join('');
}
function shift(hex, other, need, dir) {
  let [r, g, b] = hex.slice(1).match(/../g).map((h) => parseInt(h, 16));
  for (let i = 0; i < 120; i++) {
    const c = toHex(r, g, b);
    if (ratio(c, other) >= need) return c;
    if (dir === 'darker') { r *= 0.97; g *= 0.97; b *= 0.97; }
    else { r = r + (255 - r) * 0.05 + 1; g = g + (255 - g) * 0.05 + 1; b = b + (255 - b) * 0.05 + 1; }
  }
  return dir === 'darker' ? '#000000' : '#ffffff';
}

const DARK_INK = '#0b1220';                 /* 밝은 배지 위 글자색 — 사이트 기본 배경색과 같다 */
const RULE_RE = /([^{}@]+)\{([^{}]*)\}/g;

function declRe(prop) {
  return new RegExp('((?:^|;)\\s*' + prop + '\\s*:\\s*)([^;!}]+)', 'i');
}
function getDecl(body, prop) {
  const m = body.match(declRe(prop));
  return m ? m[2].trim() : null;
}
function setDecl(body, prop, value) {
  return body.replace(declRe(prop), (all, head) => head + value);
}
function fontPx(body) {
  const raw = getDecl(body, 'font-size') || getDecl(body, 'font') || '';
  const m = String(raw).match(/(\d*\.?\d+)\s*(px|rem|em)/);
  if (!m) return null;
  return m[2] === 'px' ? parseFloat(m[1]) : parseFloat(m[1]) * 16;
}
function isBold(body) { return /bold|[7-9]00/.test(getDecl(body, 'font-weight') || ''); }

let fixed = 0;
const perFile = {};

function repairCss(text) {
  RULE_RE.lastIndex = 0;
  let out = '';
  let last = 0;
  let m;
  while ((m = RULE_RE.exec(text))) {
    const [whole, sel, body] = m;
    if (/::(before|after)/.test(sel)) continue;
    const fgRaw = getDecl(body, 'color');
    const bgProp = getDecl(body, 'background-color') ? 'background-color' : 'background';
    const bgRaw = getDecl(body, bgProp);
    const fg = parseColor(fgRaw);
    if (!fg || !bgRaw) continue;
    const bgTokens = String(bgRaw).trim().split(/\s+/);
    const bg = parseColor(bgTokens[0]);
    if (!bg) continue;

    const px = fontPx(body);
    const large = px !== null && (px >= 24 || (px >= 18.66 && isBold(body)));
    const need = large ? 3.0 : 4.5;
    if (ratio(fg, bg) >= need) continue;

    const bgBright = lum(bg) > 0.25;
    const fgBright = lum(fg) > 0.5;
    let newBody = body;
    if (bgBright && fgBright) {
      newBody = setDecl(body, 'color', DARK_INK);                       // 밝은 배지 → 어두운 글자
    } else if (!bgBright && fgBright && bgTokens.length === 1) {
      newBody = setDecl(body, bgProp, shift(bg, fg, need, 'darker'));   // 어두운 배경을 더 어둡게
    } else if (bgBright) {
      newBody = setDecl(body, 'color', shift(fg, bg, need, 'darker'));  // 밝은 배경 → 글자 어둡게
    } else {
      newBody = setDecl(body, 'color', shift(fg, bg, need, 'lighter')); // 어두운 배경 → 글자 밝게
    }
    if (newBody === body) continue;

    out += text.slice(last, m.index) + sel + '{' + newBody + '}';
    last = m.index + whole.length;
    fixed += 1;
  }
  return out + text.slice(last);
}

function processFile(rel) {
  const p = path.join(PUB, rel);
  const src = fs.readFileSync(p, 'utf8');
  let next;
  if (rel.endsWith('.css')) {
    next = repairCss(src);
  } else {
    next = src.replace(/(<style[^>]*>)([\s\S]*?)(<\/style>)/gi, (all, a, css, b) => a + repairCss(css) + b);
  }
  if (next === src) return;
  perFile[rel] = true;
  if (!DRY) fs.writeFileSync(p, next);
}

const cssDir = path.join(PUB, 'css');
if (fs.existsSync(cssDir)) {
  for (const f of fs.readdirSync(cssDir).filter((x) => x.endsWith('.css'))) processFile('css/' + f);
}
for (const f of fs.readdirSync(PUB).filter((x) => x.endsWith('.html'))) processFile(f);

console.log((DRY ? '[dry-run] ' : '') + '대비 교정 규칙 ' + fixed + '건 / 파일 ' + Object.keys(perFile).length + '개');
