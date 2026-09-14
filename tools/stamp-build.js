#!/usr/bin/env node
/* 빌드 스탬프 생성기 — 배포 전에 실행한다.
 *
 * 두 가지 문제를 한 번에 해결한다.
 *  1) sw.js 의 VERSION 이 'wvs-v1' 로 고정돼 있어 배포해도 옛 캐시가 비워지지 않는다.
 *  2) 총 항목 수가 홈(319+) · 허브 title(463) · 허브 런타임(473) 으로 제각각이다.
 *
 * 허브의 런타임 계산 로직(#menuX 안의 .list-group-item 개수)을 그대로 정적 재현해
 * public/js/build-meta.json 한 곳에 기록하고, sw.js VERSION 과 문서 내 표기를 여기에 맞춘다.
 *
 * 사용: node tools/stamp-build.js [--check]
 *   --check 는 파일을 고치지 않고 불일치만 보고한다(CI/배포 게이트용).
 */
'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const PUBLIC = path.join(ROOT, 'public');
const HUB = path.join(PUBLIC, 'vuln-hub.html');
const SW = path.join(PUBLIC, 'sw.js');
const HOME = path.join(PUBLIC, 'index.html');
const META = path.join(PUBLIC, 'js', 'build-meta.json');

const CHECK = process.argv.includes('--check');

/* 허브 스크립트의 그룹 정의와 동일하게 유지할 것 (vuln-hub.html 의 sums). */
const GROUPS = {
  A: ['menu3', 'menu4', 'menuTime', 'menuErr', 'menuCode', 'menuEncap', 'menuApi', 'menuDesign', 'menu2'],
  B: ['menu1', 'menu5', 'menu9', 'menu6', 'menu10', 'menu11', 'menu12', 'menu13'],
  C: ['menu7', 'menuSrvLab'],
  D: ['menuAI'],
  E: ['menuAuto'],
  F: ['menuPrivacy'],
  G: ['menuZT'],
};

/* id="X" 로 열리는 div 의 닫는 태그까지를 깊이 계산으로 잘라낸다. */
function sliceById(html, id) {
  const open = new RegExp('<div[^>]*\\bid="' + id + '"[^>]*>', 'i');
  const m = open.exec(html);
  if (!m) return null;
  let i = m.index + m[0].length;
  let depth = 1;
  const tag = /<\/?div\b[^>]*>/gi;
  tag.lastIndex = i;
  let t;
  while ((t = tag.exec(html)) !== null) {
    depth += t[0][1] === '/' ? -1 : 1;
    if (depth === 0) return html.slice(i, t.index);
  }
  return html.slice(i);
}

function countItems(html, id) {
  const seg = sliceById(html, id);
  if (seg === null) return { id, count: 0, missing: true };
  const m = seg.match(/class="[^"]*\blist-group-item\b/g);
  return { id, count: m ? m.length : 0, missing: false };
}

function main() {
  const hub = fs.readFileSync(HUB, 'utf8');
  const counts = {};
  const missing = [];
  let total = 0;
  for (const [g, ids] of Object.entries(GROUPS)) {
    let sum = 0;
    for (const id of ids) {
      const r = countItems(hub, id);
      if (r.missing) missing.push(id);
      sum += r.count;
    }
    /* 개인정보보호 그룹은 시뮬레이터 외에 groupF 직속 도구 링크도 센다(허브와 동일). */
    if (g === 'F') {
      const seg = sliceById(hub, 'groupF') || '';
      const tools = seg.match(/<a\b[^>]*class="[^"]*\bmenu-category\b/g);
      sum += tools ? tools.length : 0;
    }
    counts[g] = sum;
    total += sum;
  }

  const pages = fs.readdirSync(PUBLIC).filter((f) => f.endsWith('.html')).length;

  if (missing.length) console.warn('WARN 허브에서 못 찾은 메뉴 id:', missing.join(', '));

  /* ── 1. 허브 title 의 페이지 수 ── */
  const hubNew = hub.replace(/(<title>[^<]*?)\d+(페이지 학습 허브)/, '$1' + pages + '$2');
  const hubChanged = hubNew !== hub;

  /* ── 2. 홈의 실습 개수 ── */
  const home = fs.readFileSync(HOME, 'utf8');
  const homeNew = home.replace(/\d+개\+ 인터랙티브 공격·방어 실습/g, total + '개+ 인터랙티브 공격·방어 실습');
  const homeChanged = homeNew !== home;

  /* ── 3. 스탬프 = '배포될 내용'의 해시 ──
     커밋 해시를 쓰면 stamp → commit → 해시 변화 → 다시 drift 가 되어 게이트가 영원히 실패한다.
     내용 해시는 실제로 파일이 바뀔 때만 달라지므로 캐시 무효화 목적에도 정확히 맞는다.
     한 번에 수렴하려면 (a) 이 도구가 스스로 고쳐 쓰는 hub/home 은 '수정 후' 내용으로 해시하고,
     (b) 해시 결과를 담는 sw.js·build-meta.json 은 해시 대상에서 뺀다. */
  const SELF = new Set(['sw.js', path.join('js', 'build-meta.json')]);
  const OVERRIDE = new Map([
    [path.basename(HUB), hubNew],
    [path.basename(HOME), homeNew],
  ]);
  const h = crypto.createHash('sha256');
  const walk = (dir, rel) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name < b.name ? -1 : 1)) {
      const r = rel ? path.join(rel, e.name) : e.name;
      if (SELF.has(r)) continue;
      const p = path.join(dir, e.name);
      if (e.isDirectory()) { walk(p, r); continue; }
      h.update(r);
      const ov = OVERRIDE.get(r);
      h.update(ov !== undefined ? Buffer.from(ov, 'utf8') : fs.readFileSync(p));
    }
  };
  walk(PUBLIC, '');
  /* 날짜를 붙이면 내용이 그대로여도 다음 날 drift 로 잡히므로 순수 내용 해시만 쓴다.
     사람이 볼 생성 시각은 build-meta.json 의 generatedAt 에 남는다. */
  const stamp = 'wvs-' + h.digest('hex').slice(0, 12);
  const meta = {
    buildId: stamp,
    generatedAt: new Date().toISOString(),
    pages,
    catalogTotal: total,
    groups: counts,
    note: '이 파일은 tools/stamp-build.js 가 생성한다. 직접 수정하지 말 것.',
  };

  const sw = fs.readFileSync(SW, 'utf8');
  const swNew = sw.replace(/var VERSION = '[^']*';/, "var VERSION = '" + stamp + "';");
  const swChanged = swNew !== sw;

  if (CHECK) {
    const drift = [];
    if (swChanged) drift.push('sw.js VERSION 이 현재 빌드와 다름');
    if (hubChanged) drift.push('vuln-hub.html title 의 페이지 수가 실제(' + pages + ')와 다름');
    if (homeChanged) drift.push('index.html 실습 개수가 실제(' + total + ')와 다름');
    let metaDrift = true;
    try {
      const cur = JSON.parse(fs.readFileSync(META, 'utf8'));
      metaDrift = cur.catalogTotal !== total || cur.pages !== pages;
    } catch (e) { /* 없으면 drift */ }
    if (metaDrift) drift.push('build-meta.json 의 수치가 실제와 다름');
    if (drift.length) {
      console.error('build stamp drift:\n  - ' + drift.join('\n  - '));
      console.error('  → node tools/stamp-build.js 를 실행해 갱신하세요.');
      process.exit(1);
    }
    console.log('build stamp OK  pages=' + pages + ' catalogTotal=' + total);
    return;
  }

  fs.writeFileSync(META, JSON.stringify(meta, null, 2) + '\n', 'utf8');
  if (swChanged) fs.writeFileSync(SW, swNew, 'utf8');
  if (hubChanged) fs.writeFileSync(HUB, hubNew, 'utf8');
  if (homeChanged) fs.writeFileSync(HOME, homeNew, 'utf8');

  console.log('build stamp: ' + stamp);
  console.log('  pages        ' + pages);
  console.log('  catalogTotal ' + total + '  ' + JSON.stringify(counts));
  console.log('  updated: build-meta.json' +
    (swChanged ? ', sw.js' : '') + (hubChanged ? ', vuln-hub.html' : '') + (homeChanged ? ', index.html' : ''));
}

main();
