#!/usr/bin/env node
/**
 * [C05] 대표 체험 안정성 검사.
 *
 * 재평가 문서 §10 C05: "새 방문/재방문, API 실패, URL 직접 접근 확인".
 * §2: 심사 기간 내내 서비스에 접속 가능해야 한다.
 *
 * 여기서 막으려는 것은 "화면에 오류가 안 나면서 시연만 죽는" 경우다.
 *   - 심사위원이 홈을 거치지 않고 incident.html 로 바로 들어온다
 *   - 예전에 한 번 와서 옛 형식의 localStorage 가 남아 있다
 *   - AI 프록시가 막혀 있거나 키가 없다
 *   - 배포 직후 서비스 워커가 옛 자산을 물고 있다
 *
 * 실행: node tools/test-experience-stability.js
 */
'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const PUB = path.join(ROOT, 'public');
const read = (p) => fs.readFileSync(path.join(PUB, p), 'utf8');
const exists = (p) => fs.existsSync(path.join(PUB, p));

let pass = 0;
const ok = (n) => { console.log('  PASS  ' + n); pass++; };

/* 제출 시연에 반드시 살아 있어야 하는 경로 */
const DEMO_PAGES = [
  'index.html',
  'incident.html',
  'coach-eval.html',
  'vuln-hub.html',
  'my-progress.html',
];

(async () => {
  /* ── 1) URL 직접 접근 — 시연 페이지가 단독으로 성립하는가 ── */
  DEMO_PAGES.forEach((p) => {
    assert.ok(exists(p), p + ' 이(가) 없다');
  });
  /* incident 는 홈을 거치지 않아도 자기 자원만으로 떠야 한다 */
  const inc = read('incident.html');
  ['incident-engine.js', 'coach.js'].forEach((dep) => {
    assert.ok(inc.includes(dep), 'incident.html 이 ' + dep + ' 을 싣지 않는다');
    assert.ok(exists('js/' + dep), 'js/' + dep + ' 파일이 없다');
  });
  /* 홈에서 넘어올 때만 세팅되는 전역에 의존하면 직접 접근이 깨진다 */
  assert.ok(!/sessionStorage\.getItem\(['"]wvs_from_home/.test(inc),
    'incident.html 이 홈 경유 여부에 의존한다');
  ok('URL 직접 접근 — 시연 페이지 5종이 단독으로 성립');

  /* ── 2) 새 방문 — 저장된 상태가 전혀 없을 때 ── */
  const store = {};
  global.localStorage = {
    getItem: (k) => (k in store ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v); },
    removeItem: (k) => { delete store[k]; },
  };
  global.window = global;
  global.fetch = async () => ({ ok: true, json: async () => ({ items: [] }) });

  const INC = require(path.join(PUB, 'js', 'incident-engine.js'));
  assert.strictEqual(INC.stages.length, 4, '단계 4개');
  /* 아무 입력도 없는 상태에서 채점해도 예외가 나면 안 된다 */
  INC.stages.forEach((s) => {
    const r = INC.grade(s.id, null);
    assert.ok(r && Array.isArray(r.results), s.id + ': 빈 입력 채점이 결과를 안 준다');
    assert.strictEqual(r.passed, false, s.id + ': 빈 입력이 통과로 처리됐다');
  });
  /* 증거는 새 방문자에게도 바로 읽혀야 한다 */
  INC.stages.forEach((s) => {
    s.evidenceIds.forEach((id) => {
      const e = INC.evidence(id);
      assert.ok(e && e.label && e.body.length, s.id + ' 의 증거 ' + id + ' 에 내용이 없다');
      assert.ok(!/^ev-/.test(e.label), '증거 제목이 내부 ID 다: ' + id);
    });
  });
  ok('새 방문 — 저장 상태 없이 채점·증거 열람이 성립');

  /* ── 3) 재방문 — 옛/깨진 localStorage 를 물고 들어온 경우 ── */
  eval(fs.readFileSync(path.join(PUB, 'js', 'coach.js'), 'utf8'));
  const COACH = global.WVS_COACH;

  const BROKEN = [
    'not json at all',
    '{"불완전":',
    '[]',
    'null',
    '{"api-authz":{"answer":{"conds":null}}}',        /* 형태가 바뀐 예전 답안 */
    '{"api-authz":{"answer":{"join":"or"}}}',          /* conds 자체가 없음 */
  ];
  BROKEN.forEach((raw) => {
    store.wvs_incident = raw;
    /* incident.html 의 load() 와 같은 방식 */
    let st;
    try { st = JSON.parse(localStorage.getItem('wvs_incident')) || {}; } catch (e) { st = {}; }
    assert.ok(typeof st === 'object', '깨진 저장값에서 객체를 못 만든다: ' + raw.slice(0, 20));
    /* 그 상태로 코치 맥락을 만들어도 예외가 없어야 한다 */
    const c = COACH.buildContext({
      activityId: 'incident:api-authz',
      learnerPolicy: (st['api-authz'] || {}).answer,
      failedChecks: [],
    });
    assert.ok(c.activityId, '깨진 상태에서 코치 맥락 생성 실패');
  });
  delete store.wvs_incident;
  ok('재방문 — 깨지거나 옛 형식인 저장값 6종에서 계속 진행 가능');

  /* ── 4) API 실패 — AI 가 없거나 막혔을 때 ── */
  const ctx = COACH.buildContext({
    activityId: 'incident:api-authz',
    successCondition: '정상 3건 허용, 비인가 3건 거부',
    failedChecks: [{ id: 's1-other-read', desc: '타인이 남의 차량 조회',
      expected: '거부', actual: '허용', meaning: '거부돼야 하는 요청이 아직 허용된다.' }],
  });

  /* (a) WVS_AI 자체가 없음 */
  delete global.WVS_AI;
  let r = await COACH.ask(ctx);
  assert.ok(r.ok && r.coach.observation, 'AI 없음: 안내가 비었다');
  assert.strictEqual(r.coach.mode, 'static');

  /* (b) 호출이 예외를 던짐 */
  global.WVS_AI = { chat: async () => { throw new Error('network down'); } };
  r = await COACH.ask(ctx);
  assert.ok(r.ok && r.coach.observation, '예외: 안내가 비었다');
  assert.strictEqual(r.fellBack, 'exception');

  /* (c) 프록시가 오류 코드를 돌려줌 */
  global.WVS_AI = { chat: async () => ({ ok: false, proxyError: 'HTTP 501' }) };
  r = await COACH.ask(ctx);
  assert.ok(r.ok && r.coach.observation, '프록시 오류: 안내가 비었다');
  assert.ok(r.fellBack, '폴백 원인이 기록되지 않음');

  /* (d) 응답이 계약과 다른 모양 */
  global.WVS_AI = { chat: async () => ({ ok: true, json: { nope: 1 } }) };
  r = await COACH.ask(ctx);
  assert.strictEqual(r.coach.mode, 'static', '잘못된 모양인데 AI 응답으로 채택');

  /* 어떤 실패에서도 "기본 도움말" 이라고 밝혀야 한다 */
  assert.ok(/기본 도움말/.test(r.coach.uncertainty), '폴백을 실시간 AI 처럼 보여준다');
  delete global.WVS_AI;
  ok('API 실패 4종 — 실습이 멈추지 않고, 기본 도움말임을 밝힌다');

  /* ── 5) 배포 직후 — 서비스 워커가 옛 자산을 물지 않는가 ── */
  const sw = read('sw.js');
  const meta = JSON.parse(read('js/build-meta.json'));
  const m = sw.match(/VERSION\s*=\s*['"]([^'"]+)['"]/);
  assert.ok(m, 'sw.js 에서 VERSION 을 찾지 못함');
  assert.strictEqual(m[1], meta.buildId,
    'sw.js VERSION(' + m[1] + ') 과 build-meta buildId(' + meta.buildId + ') 가 다르다. '
    + '재방문자가 옛 자산을 물고 시연이 깨진다. node tools/stamp-build.js 를 돌린다.');

  /* 프리캐시 목록에 실제로 없는 파일이 있으면 설치가 조용히 실패한다 */
  const pre = sw.match(/PRECACHE\s*=\s*\[([\s\S]*?)\]/);
  assert.ok(pre, 'PRECACHE 목록을 찾지 못함');
  const urls = [...pre[1].matchAll(/'([^']+)'|"([^"]+)"/g)].map((x) => x[1] || x[2]);
  urls.forEach((u) => {
    if (/^https?:/.test(u)) return;
    assert.ok(exists(u.replace(/^\//, '')), '프리캐시에 없는 파일: ' + u);
  });
  ok('배포 직후 — SW 버전이 빌드와 일치하고 프리캐시 목록이 실재함');

  /* ── 6) 평가 리포트가 배포 경로에 있는가 ── */
  assert.ok(exists('data/coach-eval-report.json'),
    '평가 리포트가 public 안에 없다. docs/ 에 두면 심사 중 화면이 빈다.');
  const rep = JSON.parse(read('data/coach-eval-report.json'));
  assert.strictEqual(rep.offline.measured, true, '오프라인 평가가 측정됨으로 기록되지 않음');
  assert.strictEqual(rep.realModel.measured, false, '실제 모델 평가를 측정함으로 표시하면 안 됨');
  Object.keys(rep.realModel.metrics).forEach((k) => {
    assert.strictEqual(rep.realModel.metrics[k], null,
      '실행하지 않은 지표 ' + k + ' 에 값이 들어 있다');
  });
  ok('평가 리포트 — 배포 경로에 있고 미측정 항목이 null 로 남아 있음');

  console.log(`\nALL ${pass} CHECKS PASSED`);
})().catch((e) => {
  console.error('\nFAILED:', e && e.message);
  process.exit(1);
});
