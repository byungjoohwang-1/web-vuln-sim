#!/usr/bin/env node
/* 허브 카탈로그 검색 키워드 보강 — P1-07.
 *
 * 문제: 470개 항목 모두 data-keywords 를 갖고 있지만 값이 너무 얄팍해서
 *   "자동차" → 0건 (E-1 자동차 보안 항목이 61개나 있는데도)
 *   "쿠버네티스" → 0건, "개인정보" → 3건 (실제 37개)
 * 검색이 영어 기술용어를 이미 아는 사람에게만 동작하는 상태였다.
 *
 * 해결: 각 항목의 data-keywords 에
 *   (1) 소속 메뉴의 한글/영문 라벨  (2) 항목의 표시 텍스트  (3) 동의어
 * 를 덧붙인다. 기존 키워드는 그대로 두고 없는 토큰만 추가한다(멱등).
 *
 * 사용: node tools/enrich-hub-keywords.js [--check]
 */
'use strict';
const fs = require('fs');
const path = require('path');

const HUB = path.resolve(__dirname, '..', 'public', 'vuln-hub.html');
const CHECK = process.argv.includes('--check');

/* 한국어 검색어 → 항목에 심을 추가 토큰. 실무자가 실제로 칠 법한 말 위주. */
const SYNONYMS = {
  menuAuto: ['자동차', '차량', 'automotive', 'vehicle', 'can', 'ecu', 'uds', 'misra', '모빌리티'],
  menuAI: ['ai', '인공지능', 'llm', '생성형', '프롬프트', 'prompt', '머신러닝', '딥페이크'],
  menuPrivacy: ['개인정보', 'privacy', '가명처리', '영향평가', 'pia', '보호법'],
  menu7: ['금융', '전자금융', 'financial', 'fintech', '핀테크'],
  menu12: ['클라우드', 'cloud', '컨테이너', 'container', '쿠버네티스', 'kubernetes', 'k8s', 'docker', '도커'],
  menu13: ['제어시스템', 'ics', 'scada', 'ot', '산업제어', 'plc'],
  menu5: ['unix', 'linux', '리눅스', '유닉스', '서버', 'server'],
  menu9: ['windows', '윈도우', '서버', 'server'],
  menu6: ['dbms', '데이터베이스', 'database', 'db', 'sql'],
  menu10: ['네트워크', 'network', '라우터', 'router', '스위치', 'switch', '장비'],
  menu11: ['보안장비', '방화벽', 'firewall', 'ips', 'ids', 'waf', 'appliance'],
  menu1: ['kisa', '보안약점', 'weakness', '시뮬레이터'],
  menu2: ['개념', '가이드', 'guide', 'concept'],
  menu3: ['입력', '검증', 'input', 'validation', '표현'],
  menu4: ['보안기능', 'security', 'feature', '인증', '인가', '암호'],
  menuTime: ['시간', '상태', 'time', 'state', '경쟁조건', 'race'],
  menuErr: ['에러', '오류', 'error', 'handling', '예외', 'exception'],
  menuCode: ['코드오류', 'code', 'error', '메모리', 'memory'],
  menuEncap: ['캡슐화', 'encapsulation', '정보은닉'],
  menuApi: ['api', '오용', 'abuse', '잘못된사용'],
  menuDesign: ['설계', 'design', '아키텍처', 'architecture', '위협모델링'],
};

/* id="X" 로 열린 div 의 본문을 깊이 계산으로 잘라낸다. */
function findBlock(html, id) {
  const open = new RegExp('<div[^>]*\\bid="' + id + '"[^>]*>', 'i');
  const m = open.exec(html);
  if (!m) return null;
  const start = m.index + m[0].length;
  let depth = 1;
  const tag = /<\/?div\b[^>]*>/gi;
  tag.lastIndex = start;
  let t;
  while ((t = tag.exec(html)) !== null) {
    depth += t[0][1] === '/' ? -1 : 1;
    if (depth === 0) return { start, end: t.index };
  }
  return { start, end: html.length };
}

/* 표시 텍스트에서 검색에 쓸 만한 토큰만 추린다(번호·기호 제외). */
function textTokens(fragment) {
  const visible = fragment
    .replace(/<[^>]+>/g, ' ')
    .replace(/&[a-z]+;/gi, ' ')
    .replace(/#\d+/g, ' ');
  return visible
    .split(/[\s,·/()[\]{}:;"'|]+/)
    .map((w) => w.trim().toLowerCase())
    .filter((w) => w.length >= 2 && !/^\d+$/.test(w) && !/^[-–—.]+$/.test(w));
}

function main() {
  const orig = fs.readFileSync(HUB, 'utf8');
  let html = orig;
  let touched = 0;

  for (const menuId of Object.keys(SYNONYMS)) {
    const blk = findBlock(html, menuId);
    if (!blk) { console.warn('WARN 메뉴 없음:', menuId); continue; }
    const before = html.slice(0, blk.start);
    const after = html.slice(blk.end);
    let body = html.slice(blk.start, blk.end);

    /* 이 메뉴 안의 각 항목 <a ... class="... list-group-item ..."> ... </a> */
    body = body.replace(/<a\b([^>]*\blist-group-item\b[^>]*)>([\s\S]*?)<\/a>/gi, (full, attrs, inner) => {
      const km = /data-keywords="([^"]*)"/i.exec(attrs);
      const existing = km ? km[1] : '';
      const have = new Set(existing.toLowerCase().split(/\s+/).filter(Boolean));
      const add = [];
      for (const tok of SYNONYMS[menuId].concat(textTokens(inner))) {
        if (!have.has(tok) && !/["<>]/.test(tok)) { have.add(tok); add.push(tok); }
      }
      if (!add.length) return full;
      touched++;
      const merged = (existing ? existing + ' ' : '') + add.join(' ');
      const newAttrs = km
        ? attrs.replace(/data-keywords="[^"]*"/i, 'data-keywords="' + merged + '"')
        : attrs + ' data-keywords="' + merged + '"';
      return '<a' + newAttrs + '>' + inner + '</a>';
    });

    html = before + body + after;
  }

  if (CHECK) {
    if (html !== orig) {
      console.error('허브 검색 키워드가 최신이 아닙니다 (' + touched + '개 항목). node tools/enrich-hub-keywords.js 실행 필요.');
      process.exit(1);
    }
    console.log('허브 검색 키워드 OK');
    return;
  }

  if (html === orig) { console.log('변경 없음 (이미 최신)'); return; }
  fs.writeFileSync(HUB, html, 'utf8');
  console.log('검색 키워드 보강: ' + touched + '개 항목');
}

main();
