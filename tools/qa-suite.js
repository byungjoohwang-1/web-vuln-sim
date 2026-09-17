#!/usr/bin/env node
/* qa-suite.js — 전체 QA 일괄 실행기 (반복 실행으로 일시적 오탐을 걸러낸다)
 *
 * 왜 만들었나:
 *   배포 게이트가 같은 커밋에서 한 번은 실패하고 다음엔 통과하는 일이 있었다.
 *     - "A11Y-SHELL: 공통 셸이 없는 페이지 7개" → 실제로는 전부 갖고 있었다
 *       (병행 세션이 그 파일들을 쓰는 중이었다)
 *     - "JS syntax error" → 실은 V8 OOM. public/data/evidence/*.js 가 89MB 라
 *       메모리 경합 시 node --check 가 죽는다
 *   한 번만 돌려서는 '진짜 결함'과 '그때만 그런 것'을 구분할 수 없다.
 *   그래서 같은 검사를 N회 돌려 **매번 실패한 것만** 진짜로 본다.
 *
 * 사용법:
 *   node tools/qa-suite.js            # 3회 (기본)
 *   node tools/qa-suite.js --runs 5
 *   node tools/qa-suite.js --list     # 무엇을 돌리는지만 표시
 */
'use strict';

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = path.join(__dirname, '..');

/* cmd: 실행 파일, args: 인자. 이름은 리포트에 쓴다. */
const SUITE = [
  // 구조·무결성
  ['빌드 검증 (validate_build)', 'python', ['_gen/validate_build.py']],
  ['공개 산출물 검증 (링크·SRI·인라인문법)', process.execPath, ['tools/validate-public-site.js']],
  ['플랫폼 통합', process.execPath, ['tools/test-platform-integration.js']],
  ['접근성', process.execPath, ['tools/test-a11y.js']],
  ['체험 안정성', process.execPath, ['tools/test-experience-stability.js', '--check']],

  // 콘텐츠 랩 자체 검증
  ['보안약점 현업진단 랩', process.execPath, ['tools/test-code-lab.js']],
  ['금융 서버 진단 랩', process.execPath, ['tools/test-srv-lab.js']],
  ['정보보호시스템 진단 랩', process.execPath, ['tools/test-iss-lab.js']],

  // 채점·판정 로직
  ['AI 코치 계약', process.execPath, ['tools/eval-coach.js', '--check']],
  ['코치 응답', process.execPath, ['tools/test-coach.js']],
  ['오개념 진단', process.execPath, ['tools/test-misconception.js']],
  ['수료증 위조 검증기', process.execPath, ['tools/test-forge-verifier.js']],
  ['사건 재구성 실습', process.execPath, ['tools/test-incident.js']],
  ['Firestore 규칙', process.execPath, ['tools/test-firestore-rules.js']],

  // 개인정보 페이지
  ['개인정보 페이지', process.execPath, ['tools/check-privacy-pages.js']],

  // 생성기 드리프트
  ['수료 코드 대조', 'python', ['_gen/check_cert_codes.py']],
  ['현업진단 시나리오 스키마', 'python', ['_gen/gen_code_lab.py', '--check']],
];

function runOne(cmd, args) {
  const started = Date.now();
  const r = spawnSync(cmd, args, { cwd: ROOT, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
  const out = ((r.stdout || '') + (r.stderr || ''));
  return {
    ok: r.status === 0,
    status: r.status,
    ms: Date.now() - started,
    // 실패 원인 추정에 쓸 마지막 의미 있는 줄들
    tail: out.split(/\r?\n/).filter(l => l.trim()).slice(-4).join(' | ').slice(0, 300),
    oom: /Last few GCs|JavaScript heap out of memory/.test(out),
    spawnErr: r.error ? String(r.error.message).slice(0, 120) : null,
    // 의존 서비스가 없어서 못 돈 것과 진짜 실패를 구분한다.
    // 이걸 '결함'으로 묶으면 리포트가 거짓말을 하고, 반대로 조용히 건너뛰면
    // 보안 규칙 검사가 사실상 사라진다. 그래서 별도 상태로 드러낸다.
    envMissing: /ECONNREFUSED|ENOTFOUND|fetch failed/.test(out),
  };
}

function main() {
  const argv = process.argv.slice(2);
  if (argv.includes('--list')) {
    SUITE.forEach(([n, c, a]) => console.log(`  ${n}\n      ${path.basename(c)} ${a.join(' ')}`));
    return;
  }
  const ri = argv.indexOf('--runs');
  const RUNS = ri >= 0 ? Math.max(1, parseInt(argv[ri + 1], 10) || 3) : 3;

  // 존재하지 않는 검사기는 미리 걸러 낸다(있는 척하는 리포트 방지)
  const suite = SUITE.filter(([name, , args]) => {
    const target = args.find(a => a.endsWith('.js') || a.endsWith('.py'));
    const exists = !target || fs.existsSync(path.join(ROOT, target));
    if (!exists) console.log(`  (건너뜀) ${name} — ${target} 없음`);
    return exists;
  });

  const results = new Map();   // name -> [run1, run2, ...]
  for (let run = 1; run <= RUNS; run++) {
    console.log(`\n${'='.repeat(64)}\n  QA ${run}/${RUNS} 회차\n${'='.repeat(64)}`);
    for (const [name, cmd, args] of suite) {
      const r = runOne(cmd, args);
      if (!results.has(name)) results.set(name, []);
      results.get(name).push(r);
      const mark = r.ok ? 'PASS' : 'FAIL';
      const extra = r.oom ? ' [OOM]' : (r.spawnErr ? ' [spawn]' : '');
      console.log(`  ${mark}  ${name}  (${(r.ms / 1000).toFixed(1)}s)${extra}`);
      if (!r.ok) console.log(`        ${r.tail}`);
    }
  }

  // ── 판정 ────────────────────────────────────────────────
  console.log(`\n${'='.repeat(64)}\n  종합 (${RUNS}회 기준)\n${'='.repeat(64)}`);
  const always = [], flaky = [], clean = [], envless = [];
  for (const [name, runs] of results) {
    const fails = runs.filter(r => !r.ok).length;
    if (fails === 0) clean.push(name);
    else if (runs.every(r => r.ok || r.envMissing) && runs.some(r => r.envMissing)) {
      envless.push([name, runs]);        // 의존 서비스 미기동 — 미측정이지 통과가 아니다
    } else if (fails === RUNS) always.push([name, runs]);
    else flaky.push([name, runs, fails]);
  }

  if (envless.length) {
    console.log(`\n  ⊘ 미측정(의존 서비스 없음): ${envless.length}개 — 통과한 것이 아니다`);
    envless.forEach(([n]) => {
      console.log(`    - ${n}`);
      if (/Firestore/.test(n)) {
        console.log('        firebase emulators:start --only firestore  를 띄운 뒤 다시 돌린다');
      }
    });
  }

  console.log(`\n  항상 통과: ${clean.length}개`);
  clean.forEach(n => console.log(`    - ${n}`));

  if (flaky.length) {
    console.log(`\n  ⚠ 불안정(일부 회차만 실패): ${flaky.length}개 — 코드 결함이 아니라 환경 문제일 수 있다`);
    flaky.forEach(([n, runs, f]) => {
      const oom = runs.some(r => r.oom);
      console.log(`    - ${n}: ${f}/${RUNS}회 실패${oom ? ' [OOM 관측됨]' : ''}`);
      const first = runs.find(r => !r.ok);
      if (first) console.log(`        ${first.tail}`);
    });
  }

  if (always.length) {
    console.log(`\n  ✖ 항상 실패(진짜 결함): ${always.length}개`);
    always.forEach(([n, runs]) => {
      console.log(`    - ${n}`);
      console.log(`        ${runs[0].tail}`);
    });
  }

  const avg = [...results.values()].flat().reduce((s, r) => s + r.ms, 0) / 1000;
  console.log(`\n  총 실행 ${[...results.values()].flat().length}건 · 누적 ${avg.toFixed(0)}초`);

  // 종료 코드: '항상 실패'가 있을 때만 실패로 본다.
  // 불안정 항목으로 CI 를 빨갛게 만들면 사람들이 곧 무시하게 된다.
  // 미측정도 실패로 본다. '안 돌았다'를 '통과'로 세면 리포트가 거짓이 된다.
  process.exit((always.length || envless.length) ? 1 : 0);
}

main();
