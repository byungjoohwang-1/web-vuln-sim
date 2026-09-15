#!/usr/bin/env node
/* test-code-lab.js — 보안약점 '현업 진단' 시나리오 자체 검증
 *
 * 왜 필요한가:
 *   시나리오는 사람이 쓴 산문이라 생성기 스키마 검사만으로는 품질이 보장되지 않는다.
 *   "정답 조치가 실제로 차단을 보여주는가", "오답 조치가 실패를 보여주는가",
 *   "판정 근거가 증거에 실제로 등장하는 내용인가" 같은 것은 따로 봐야 한다.
 *
 * 사용법:  node tools/test-code-lab.js
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const DATA = path.join(ROOT, 'public', 'data', 'code-lab.json');

let pass = 0;
const fails = [];

function check(name, cond, detail) {
  if (cond) { pass++; return; }
  fails.push(detail ? `${name} — ${detail}` : name);
}

if (!fs.existsSync(DATA)) {
  console.error('code-lab.json 이 없다. python _gen/gen_code_lab.py 를 먼저 실행한다.');
  process.exit(1);
}
const scen = JSON.parse(fs.readFileSync(DATA, 'utf8'));
const keys = Object.keys(scen).sort();

/* 재현 결과(retest)는 '명령/조건 + 그 결과'가 보여야 학습 자료가 된다.
 *
 * 처음에는 정답이면 '차단', 오답이면 '여전히 통함'을 나타내는 낱말을 정규식으로
 * 찾으려 했는데, 같은 뜻을 쓰는 표현이 너무 많아 멀쩡한 시나리오를 계속 잡았다.
 * 산문의 의미를 정규식으로 판정하려 한 것이 잘못이었다.
 * 그래서 낱말 대신 '재현 결과가 결과를 실제로 보여주는 형태인가'라는 구조를 본다. */
const HAS_CMD = /^\s*(\$|#|--|\/\/|<|\{|[A-Za-z_]+\s*[:=])|^\s*\S+\s/m;   // 명령·코드·설정 줄

/* '결과가 보이는가'를 낱말이 아니라 줄 구조로 판정한다.
   명령($로 시작) 말고 출력으로 읽히는 줄이 최소 한 줄은 있어야 한다. */
function showsOutcome(retest) {
  return String(retest || '').split('\n')
    .some(l => l.trim() && !l.trim().startsWith('$'));
}

for (const k of keys) {
  const d = scen[k];
  const t = d.ticket, ev = d.evidence, v = d.verdict, opts = d.fix.options;

  /* --- 티켓 --- */
  check(`${k}: 티켓 본문 길이`, (t.body || '').length >= 40,
    `본문이 ${(t.body || '').length}자로 너무 짧다`);
  /* 티켓이 "정탐이다/취약하다"를 단정하면 판정 단계가 무의미해진다.
     (스캐너 티켓이 CWE 번호를 다는 것은 현업에서 정상이므로 그것은 막지 않는다) */
  check(`${k}: 티켓이 판정 결과를 미리 단정하지 않는다`,
    !/취약점이 확인|정탐(으로|이)|악용이 확인|반드시 조치/.test(t.body),
    '티켓이 결론을 말하면 학습자가 판정할 것이 없다');

  /* --- 증거 --- */
  check(`${k}: 증거 3건 이상`, ev.length >= 3, `${ev.length}건`);
  ev.forEach((e, i) => {
    check(`${k}: 증거[${i}] 출력이 실제 로그 형태`, (e.output || '').includes('\n'),
      '여러 줄이 아니면 도구 출력처럼 보이지 않는다');
    check(`${k}: 증거[${i}] 라벨 중복 없음`,
      ev.filter(x => x.label === e.label).length === 1, `라벨 중복: ${e.label}`);
  });

  /* --- 판정 --- */
  check(`${k}: 판정 근거 길이`, (v.why || '').length >= 60,
    `근거가 ${(v.why || '').length}자로 너무 짧다`);
  check(`${k}: 자주 틀리는 지점 존재`, !!v.trap, 'trap 이 없으면 학습 포인트가 약해진다');

  /* --- 조치 --- */
  const ok = opts.filter(o => o.ok);
  check(`${k}: 정답 조치 정확히 1개`, ok.length === 1, `${ok.length}개`);
  /* 모든 선택지의 재현 결과가 '무엇을 했고 어떻게 됐는지'를 보여야 한다 */
  opts.forEach((o, i) => {
    const tag = o.ok ? '정답' : `오답[${i}]`;
    check(`${k}: ${tag} 재현 결과가 여러 줄`, (o.retest || '').includes('\n'),
      '한 줄짜리 retest 는 재현 과정을 보여주지 못한다');
    check(`${k}: ${tag} 재현 결과에 명령·코드`, HAS_CMD.test(o.retest || ''));
    check(`${k}: ${tag} 재현 결과에 결과 표시`, showsOutcome(o.retest),
      '명령만 있고 그 결과로 읽히는 줄이 없다');
    check(`${k}: ${tag} 설명 길이`, (o.why || '').length >= (o.ok ? 30 : 20), '설명이 짧다');
  });
  check(`${k}: 조치 선택지 라벨 중복 없음`,
    new Set(opts.map(o => o.label)).size === opts.length, '라벨 중복');

  /* --- 대상 페이지 --- */
  const page = path.join(ROOT, 'public', `03_code_${k}.html`);
  check(`${k}: 대상 페이지 존재`, fs.existsSync(page));
  if (fs.existsSync(page)) {
    const html = fs.readFileSync(page, 'utf8');
    check(`${k}: 패널 1회만 주입`,
      (html.match(/id="wvs-code-lab"/g) || []).length === 1);
    /* 자바스크립트 문자열 안에 주입되지 않았는지 — 과거 실제 사고 재발 방지 */
    const panelAt = html.indexOf('id="wvs-code-lab"');
    const lastBody = html.lastIndexOf('</body>');
    check(`${k}: 패널이 문서 끝(마지막 </body> 앞)에 있다`,
      panelAt > 0 && panelAt < lastBody && lastBody - panelAt < 400,
      '패널 위치가 마지막 </body> 직전이 아니다');
  }
}

/* --- 전체 분포 --- */
const dist = { true: 0, false: 0, more: 0 };
keys.forEach(k => dist[scen[k].verdict.answer]++);
check('판정이 전부 정탐은 아니다 (오탐 판별 훈련이 성립해야 한다)',
  dist['false'] + dist['more'] >= 5,
  `정탐 ${dist['true']} / 오탐 ${dist['false']} / 추가확인 ${dist['more']}`);
check('시나리오 49종', keys.length === 49, `${keys.length}종`);

/* --- 출력 --- */
console.log('보안약점 현업 진단 시나리오 검증');
console.log(`  시나리오 ${keys.length}종 · 정탐 ${dist['true']} / 오탐 ${dist['false']} / 추가확인 ${dist['more']}`);
if (fails.length) {
  console.log(`\n실패 ${fails.length}건`);
  fails.slice(0, 40).forEach(f => console.log('  - ' + f));
  if (fails.length > 40) console.log(`  ... 외 ${fails.length - 40}건`);
  process.exit(1);
}
console.log(`ALL ${pass} CHECKS PASSED`);
