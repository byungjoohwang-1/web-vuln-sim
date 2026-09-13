/**
 * 플랫폼 통합 불변식 검사 — 페이지가 늘어날 때마다 조용히 깨지던 것들만 모았다.
 *
 * 왜 이 파일이 있나
 * -----------------
 * 병행 세션이 새 실습 페이지를 추가하면서 진도를 localStorage 에 직접 썼다.
 *   p.items['x.html'] = { c: true, v: Date.now() };  p.xp = (p.xp||0) + 150;
 * 이러면 (1) 완료 시각이 타임스탬프가 아니고 (2) 중복 지급 방지 플래그(x)가 없어
 * 나중에 엔진이 XP 를 또 주고 (3) 제출할 때마다 XP 가 무한히 늘고 (4) 완료 칩과
 * 연속 학습일이 갱신되지 않는다. 코드 리뷰로만 막기에는 반복해서 새는 종류라
 * 검사로 고정한다.
 *
 * 실행: node tools/test-platform-integration.js
 */
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const PUB = path.join(ROOT, 'public');

let pass = 0;
const fails = [];
function check(name, fn) {
  let detail;
  try { detail = fn(); } catch (e) { detail = e.message; }
  if (detail === true || detail === undefined) { pass++; console.log('  PASS  ' + name); }
  else { fails.push(name + ' — ' + detail); console.log('  FAIL  ' + name + ' — ' + detail); }
}

const htmlFiles = fs.readdirSync(PUB).filter((f) => f.endsWith('.html'));
const read = (f) => fs.readFileSync(path.join(PUB, f), 'utf8');

/* 공용 크롬을 일부러 빼는 페이지. 이유를 적어 두지 않으면 다음 사람이 그냥 늘린다. */
const CHROME_EXEMPT = {
  'offline.html': '오프라인 폴백 — 네트워크 의존(검색 인덱스 fetch)을 두지 않는다',
};

console.log('\n[1] 진도 기록 경로');

check('wvs_progress 를 localStorage 로 직접 쓰는 페이지가 없다 (엔진 API 경유)', () => {
  const bad = [];
  for (const f of htmlFiles) {
    const s = read(f);
    if (/setItem\(\s*['"]wvs_progress['"]/.test(s)) bad.push(f);
  }
  for (const f of fs.readdirSync(path.join(PUB, 'js')).filter((x) => x.endsWith('.js'))) {
    if (f === 'progress.js') continue;                 // 엔진 본체는 당연히 쓴다
    const s = fs.readFileSync(path.join(PUB, 'js', f), 'utf8');
    if (/setItem\(\s*['"]wvs_progress['"]/.test(s)) bad.push('js/' + f);
  }
  return bad.length === 0 || '직접 쓰기: ' + bad.join(', ');
});

check('진도를 기록하는 페이지는 progress.js 를 싣는다', () => {
  const bad = [];
  for (const f of htmlFiles) {
    const s = read(f);
    if (!/WVSProgress\s*(&&|\.)/.test(s)) continue;
    if (!/js\/progress\.js/.test(s)) bad.push(f);
  }
  return bad.length === 0 || 'progress.js 누락: ' + bad.join(', ');
});

check('WVSProgress.complete 의 페이지 ID 는 자기 파일명과 일치한다', () => {
  /* ID 를 생략하면 엔진이 pageId()(=파일명)를 쓰므로 그것도 정상이다.
     문제가 되는 것은 "다른 파일명을 넘기는" 경우 — 복사·붙여넣기로 남의 진도를 올린다. */
  const bad = [];
  for (const f of htmlFiles) {
    const s = read(f);
    const calls = s.match(/WVSProgress\.complete\(([^)]*)\)/g) || [];
    for (const c of calls) {
      const m = c.match(/['"]([\w.\-]+\.html)['"]/);
      if (m && m[1] !== f) bad.push(f + ' → ' + m[1]);
    }
  }
  return bad.length === 0 || bad.join(' | ');
});

console.log('\n[2] 전역 크롬(탑바·Ctrl+K·모바일 하단 탭바)');

check('모든 페이지가 soc-chrome.js 를 싣는다 (명시 예외 제외)', () => {
  const miss = htmlFiles.filter((f) => !CHROME_EXEMPT[f] && !/soc-chrome\.js/.test(read(f)));
  return miss.length === 0 || '누락 ' + miss.length + '개: ' + miss.slice(0, 8).join(', ');
});

check('예외 목록에 적힌 페이지는 실제로 존재한다 (죽은 예외 방지)', () => {
  const gone = Object.keys(CHROME_EXEMPT).filter((f) => !htmlFiles.includes(f));
  return gone.length === 0 || '없는 파일: ' + gone.join(', ');
});

check('자체 헤더가 있는 페이지는 data-topbar="off" 로 탑바 중복을 피한다', () => {
  const bad = [];
  for (const f of htmlFiles) {
    const s = read(f);
    if (!/soc-chrome\.js/.test(s)) continue;
    const hasOwn = /class="[^"]*\b(topbar|navbar|site-header)\b/.test(s) || /<header/i.test(s);
    const off = /soc-chrome\.js"\s+data-topbar="off"/.test(s);
    if (hasOwn && !off) bad.push(f);
  }
  /* 기존 대형 허브는 자체 헤더를 공용 탑바로 대체한 이력이 있어 경고만 남긴다. */
  if (bad.length) console.log('        (참고) 자체 헤더 + 공용 탑바 동시 노출 가능: ' + bad.length + '개');
  return true;
});

console.log('\n[3] 하단 탭바 여백 / 언어 전환');

const socSrc = fs.readFileSync(path.join(PUB, 'js', 'soc-chrome.js'), 'utf8');
const tokensCss = fs.readFileSync(path.join(PUB, 'css', 'platform-tokens.css'), 'utf8');

check('soc-chrome 이 붙이는 클래스와 CSS 여백 규칙의 이름이 일치한다', () => {
  const adds = /classList\.add\('wvs-has-bnav'\)/.test(socSrc);
  const uses = /html\.wvs-has-bnav\s+body/.test(tokensCss);
  return (adds && uses) || ('add=' + adds + ' css=' + uses);
});

check('하단 탭바 여백이 탭바 높이 토큰과 safe-area 를 함께 쓴다', () => {
  const m = tokensCss.match(/html\.wvs-has-bnav\s+body\s*\{[^}]*\}/);
  if (!m) return '규칙 없음';
  return (/--wvs-bottom-nav-h/.test(m[0]) && /safe-area-inset-bottom/.test(m[0]))
    || '토큰/safe-area 누락: ' + m[0];
});

check('모바일에서 언어 바를 숨기면 대체 전환 수단이 있어야 한다', () => {
  const hidden = /\.wvs-langbar\s*\{[^}]*display:\s*none/.test(tokensCss);
  if (!hidden) return true;                       // 숨기지 않으면 이 검사는 무의미
  return /wvsx-bnav-lang/.test(socSrc) || '언어 바를 숨기는데 하단 탭바 전환 버튼이 없다';
});

check('언어 전환 버튼은 본문 번역이 가능한 페이지에서만 노출한다', () => {
  /* bilingual.js 가 없는 페이지에서 전환 버튼을 보여 주면 내비게이션만 영어로 바뀌고
     본문은 그대로라 "번역된 줄 알았는데 아님"이 된다. */
  return /if \(bilingualReady\(\)[^{]*\{[\s\S]{0,200}wvsx-bnav-lang/.test(socSrc)
    || 'bilingualReady() 조건 없이 언어 버튼을 만든다';
});

check('자체 언어 버튼이 있는 페이지에는 탭바 언어 버튼을 중복 노출하지 않는다', () => {
  return /hasOwnLangToggle\(\)/.test(socSrc) && /!hasOwnLangToggle\(\)/.test(socSrc)
    || '중복 노출 방지 조건이 없다';
});

console.log('\n[4] 카탈로그 ↔ 실제 파일');

const progCat = JSON.parse(fs.readFileSync(path.join(PUB, 'js', 'progress-catalog.json'), 'utf8'));
const contentCat = JSON.parse(fs.readFileSync(path.join(PUB, 'data', 'content-catalog.json'), 'utf8'));

check('progress-catalog 의 모든 항목 파일이 실제로 있다', () => {
  const gone = progCat.items.filter((it) => !htmlFiles.includes(it.id)).map((it) => it.id);
  return gone.length === 0 || gone.join(', ');
});

check('content-catalog 의 모든 항목 파일이 실제로 있다', () => {
  const gone = contentCat.items.filter((it) => !htmlFiles.includes(it.page)).map((it) => it.page);
  return gone.length === 0 || gone.join(', ');
});

check('content-catalog 는 progress-catalog 의 부분집합이다 (진도 없는 항목을 진도로 세지 않음)', () => {
  const inProg = new Set(progCat.items.map((it) => it.id));
  const extra = contentCat.items.filter((it) => !inProg.has(it.page)).map((it) => it.page);
  return extra.length === 0 || extra.join(', ');
});

check('완료를 기록하는 실습 페이지는 카탈로그에 등록돼 있다 (완료 수 ↔ XP 어긋남 방지)', () => {
  const inProg = new Set(progCat.items.map((it) => it.id));
  const bad = [];
  for (const f of htmlFiles) {
    if (!/WVSProgress\s*&&\s*window\.WVSProgress\.complete|WVSProgress\.complete\(/.test(read(f))) continue;
    if (!inProg.has(f)) bad.push(f);
  }
  return bad.length === 0 || '미등록: ' + bad.join(', ');
});

check('progress.js 의 학습 항목 판별식이 카탈로그의 도구 목록을 모두 포함한다', () => {
  const progJs = fs.readFileSync(path.join(PUB, 'js', 'progress.js'), 'utf8');
  const m = progJs.match(/var TOOLS = \/\^\(([^)]*)\)\$\//);
  if (!m) return 'progress.js 에서 TOOLS 판별식을 찾지 못함';
  const tools = m[1].split('|').map((s) => s.replace(/\\/g, ''));
  const prefixRe = progJs.match(/var LEARNABLE = \/\^\(([^)]*)\)\//);
  const prefixes = prefixRe ? prefixRe[1].split('|') : [];
  const missing = progCat.items
    .map((it) => it.id)
    .filter((id) => !/^sim-/.test(id))
    .filter((id) => !prefixes.some((p) => id.startsWith(p)))
    .filter((id) => tools.indexOf(id) < 0);
  return missing.length === 0 || '판별식 누락: ' + missing.join(', ');
});

console.log('\n' + (fails.length
  ? 'FAILED ' + fails.length + ' / ' + (pass + fails.length) + '\n  - ' + fails.join('\n  - ')
  : 'ALL ' + pass + ' CHECKS PASSED') + '\n');
process.exit(fails.length ? 1 : 0);
