#!/usr/bin/env node
/* 정보보호시스템(보안장비) 진단 실습 검증.
 *
 * 여기서 잡으려는 것
 *  - 조치를 적용했는데 판정이 안 바뀌는 미션 (말로만 고치는 실습)
 *  - 근거 보기에 없는 정답 (고를 수 없는 문제)
 *  - 오타 난 show 명령 (버튼을 눌러도 % Invalid 가 뜨는 문제)
 *  - '양호'로 설계한 항목이 실제로는 '취약'으로 판정되는 경우
 *  - 조치가 다른 항목의 판정을 망가뜨리는 경우 (항목 간 간섭)
 */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const PUBLIC = path.join(__dirname, '..', 'public');
let pass = 0, fail = 0;
function ok(msg) { pass++; console.log('  PASS  ' + msg); }
function no(msg) { fail++; console.log('  FAIL  ' + msg); }

function load(dataFile) {
  const sandbox = { window: {}, console };
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(path.join(PUBLIC, 'js', 'iss-lab.js'), 'utf8'), sandbox);
  vm.runInContext(fs.readFileSync(path.join(PUBLIC, 'js', dataFile), 'utf8'), sandbox);
  return { L: sandbox.window.WVS_ISS_LAB, D: sandbox.window.ISS_LAB_DATA };
}

const LABS = [
  { data: 'iss-lab-acct.js', page: '07_iss-account.html', label: '계정·인증' },
  { data: 'iss-lab-access.js', page: '07_iss-access.html', label: '접근 통제' },
  { data: 'iss-lab-log.js', page: '07_iss-log.html', label: '로그·백업·시각' },
  { data: 'iss-lab-ops.js', page: '07_iss-ops.html', label: '운영·패치' },
];

console.log('\n정보보호시스템 진단 실습 검증\n');

let totalMissions = 0;
const seenIds = new Set();

for (const lab of LABS) {
  const { L, D } = load(lab.data);
  console.log(`[${lab.data}] ${D.missions.length}개 항목 · 장비 ${D.device.name} (${D.device.type})`);
  totalMissions += D.missions.length;

  if (!fs.existsSync(path.join(PUBLIC, lab.page))) no(`${lab.page} 가 없다`);

  const cli0 = new L.Cli(new L.Config(D.cfg), D.device);
  const valid = new Set(cli0.commands());

  for (const m of D.missions) {
    const tag = `${m.id} ${m.title}`;

    // 1. 근거가 보기 안에 있어야 고를 수 있다
    const missing = (m.evidence || []).filter((e) => (m.options || []).indexOf(e) < 0);
    if (missing.length) no(`${tag} — 근거가 보기에 없다: ${missing.join(' / ')}`);

    // 2. 근거가 하나도 없으면 채점이 성립하지 않는다
    if (!m.evidence || !m.evidence.length) no(`${tag} — 근거가 비어 있다`);

    // 3. show 명령이 실제로 동작해야 한다
    for (const c of m.cmds || []) {
      if (!valid.has(c)) { no(`${tag} — 정의되지 않은 명령: ${c}`); continue; }
      const cfgT = new L.Config(D.cfg);
      const outp = new L.Cli(cfgT, D.device).run(c);
      if (!outp || /^%/.test(outp)) no(`${tag} — 명령이 거절됨: ${c}`);
    }

    // 4. 초기 판정 — fix 가 없는 항목은 '양호'로 설계된 것이다
    const cfg = new L.Config(D.cfg);
    const before = m.verdict(cfg);
    if (!m.fix) {
      if (before !== 'good') no(`${tag} — 조치가 없는데 초기 판정이 '${before}' (양호로 설계된 항목이어야 한다)`);
      else ok(`${tag} — 양호 항목이 실제로 양호로 판정된다`);
    } else {
      if (before !== 'vuln') {
        no(`${tag} — 조치가 있는데 초기 판정이 '${before}' (취약이어야 조치할 것이 있다)`);
      } else {
        // 5. 조치를 적용하면 판정이 실제로 바뀌어야 한다
        m.fix(cfg);
        const after = m.verdict(cfg);
        if (after !== 'good') no(`${tag} — 조치 후에도 판정이 '${after}' (조치가 효과 없음)`);
        else ok(`${tag} — 조치하면 취약→양호로 바뀐다`);

        // 6. 조치 후 show 출력이 실제로 달라져야 한다 (말로만 고치지 않았는지)
        const c0 = new L.Config(D.cfg);
        const outBefore = new L.Cli(c0, D.device).run(m.cmds[0]);
        const outAfter = new L.Cli(cfg, D.device).run(m.cmds[0]);
        if (outBefore === outAfter) {
          no(`${tag} — 조치 후 '${m.cmds[0]}' 출력이 그대로다`);
        }
      }
    }

    // 7. 채점기가 정답을 통과시키는지 (모범답안이 자기 루브릭을 통과하는가)
    const cfgG = new L.Config(D.cfg);
    const g = L.grade(m, cfgG, m.verdict(cfgG), m.evidence);
    if (!g.pass) no(`${tag} — 정답 제출이 채점을 통과하지 못한다`);

    // 8. 근거를 하나 더 고르면 떨어져야 한다 (다 찍으면 통과되는 문제 방지)
    const extra = (m.options || []).filter((o) => m.evidence.indexOf(o) < 0)[0];
    if (extra) {
      const g2 = L.grade(m, cfgG, m.verdict(cfgG), m.evidence.concat([extra]));
      if (g2.pass) no(`${tag} — 근거를 더 골라도 통과된다 (전부 체크하면 정답)`);
    }

    // 9. 항목 ID 중복 금지
    const key = lab.data + '::' + m.id;
    if (seenIds.has(key)) no(`${tag} — 같은 랩에 ID 가 중복된다`);
    seenIds.add(key);

    // 10. 위험도는 평가표와 같은 1~5 범위
    if (!(m.risk >= 1 && m.risk <= 5)) no(`${tag} — 위험도 ${m.risk} 가 1~5 범위를 벗어난다`);
  }

  // 11. 항목 간 간섭 — 모든 조치를 적용한 뒤 모든 항목이 양호여야 한다
  const cfgAll = new L.Config(D.cfg);
  D.missions.forEach((m) => { if (m.fix) m.fix(cfgAll); });
  const stillBad = D.missions.filter((m) => m.verdict(cfgAll) !== 'good');
  if (stillBad.length) {
    no(`전체 조치 후에도 취약인 항목: ${stillBad.map((m) => m.id).join(', ')} (조치끼리 간섭)`);
  } else {
    ok('모든 조치를 적용하면 모든 항목이 양호가 된다 (조치 간 간섭 없음)');
  }

  // 12. running-config 가 모든 단면을 담아야 한다
  const rc = new L.Cli(new L.Config(D.cfg), D.device).run('show running-config');
  const sections = ['ADMIN', 'PASSWORD-POLICY', 'MANAGEMENT', 'SNMP', 'LOGGING', 'POLICY'];
  const lost = sections.filter((s) => rc.indexOf(s) < 0);
  if (lost.length) no(`running-config 에 빠진 단면: ${lost.join(', ')}`);
  else ok('show running-config 가 주요 단면을 모두 담는다');

  // 12b. 표 출력의 열이 서로 붙지 않아야 한다
  //      "2026-09-15 08:41:122023-11-02" 처럼 값 두 개가 한 덩어리로 보이던 버그가 있었다.
  //      머리글의 열 개수와 각 데이터 행의 공백 구분 토큰 수를 맞춰 본다.
  {
    // 값의 토큰 수가 행마다 같은 표만 본다. (show session 은 "10 min"/"never" 로
    // 토큰 수가 달라져 이 방식이 안 맞는다 — 대신 아래 글루 검사로 잡는다.)
    const TABLES = {
      'show admin': { head: 'NAME', cols: 6 },   // 시각이 '날짜 시간' 두 토큰이라 6
      'show management': { head: 'PROTOCOL', cols: 4 },
      'show interface': { head: 'NAME', cols: 4 },
    };
    let collided = [];
    for (const cmd of Object.keys(TABLES)) {
      const spec = TABLES[cmd];
      const body = new L.Cli(new L.Config(D.cfg), D.device).run(cmd);
      const lines = body.split('\n');
      const hi = lines.findIndex((l) => l.indexOf(spec.head) === 0);
      if (hi < 0) continue;
      for (let i = hi + 2; i < lines.length; i++) {
        const l = lines[i];
        if (!l.trim() || /^[-]+$/.test(l.trim()) || l.indexOf(':') >= 0) break;
        const n = l.trim().split(/\s+/).length;
        if (n !== spec.cols) collided.push(`${cmd} → "${l.trim()}" (토큰 ${n}, 기대 ${spec.cols})`);
      }
    }
    // 모든 show 출력에 대해 "값 두 개가 붙어 버린" 서명을 직접 찾는다.
    // 원래 버그가 시각 뒤에 날짜가 곧바로 붙은 형태였다.
    const GLUE = [
      { re: /\d{2}:\d{2}:\d{2}\d/, what: '시각 뒤에 숫자가 바로 붙음' },
      { re: /\d{4}-\d{2}-\d{2}\d/, what: '날짜 뒤에 숫자가 바로 붙음' },
      { re: /[a-z]\d{4}-\d{2}-\d{2}/, what: '문자 뒤에 날짜가 바로 붙음' },
    ];
    for (const cmd of new L.Cli(new L.Config(D.cfg), D.device).commands()) {
      const body = new L.Cli(new L.Config(D.cfg), D.device).run(cmd) || '';
      body.split('\n').forEach((l) => {
        GLUE.forEach((g) => {
          if (g.re.test(l)) collided.push(`${cmd} → "${l.trim()}" (${g.what})`);
        });
      });
    }
    if (collided.length) no(`표의 열이 붙어 있다:\n        ${collided.join('\n        ')}`);
    else ok('표 출력의 열이 서로 붙지 않는다');
  }

  // 13. 축약 입력이 실제 장비처럼 동작해야 한다
  const cliA = new L.Cli(new L.Config(D.cfg), D.device);
  if (cliA.run('sh ver') !== cliA.run('show version')) no('축약형 "sh ver" 가 "show version" 과 다르다');
  else ok('축약형 입력이 정식 명령과 같은 출력을 낸다');

  // 14. 모르는 명령은 거절해야 한다 (아무거나 받아 주면 명령을 배울 수 없다)
  if (!/^%/.test(cliA.run('show nonexistent'))) no('없는 명령을 거절하지 않는다');
  else ok('정의되지 않은 명령을 거절한다');

  console.log('');
}

// 15. 평가대상(N/A) 처리
{
  const { L } = load(LABS[0].data);
  const m = { appliesTo: ['IDS', 'IPS'] };
  if (L.applies(m, 'FW')) no('평가대상이 아닌 장비를 대상으로 판단한다');
  else if (!L.applies(m, 'IPS')) no('평가대상인 장비를 대상이 아니라고 판단한다');
  else if (!L.applies({}, 'FW')) no('appliesTo 가 없으면 전체 대상이어야 한다');
  else ok('평가대상(장비 종류)에 따른 해당없음 판정이 동작한다');
}

console.log(`\n${fail ? 'FAILED ' + fail + ' / ' + (pass + fail) : 'ALL ' + pass + ' CHECKS PASSED'}  (${totalMissions}개 점검 항목)\n`);
process.exit(fail ? 1 : 0);
