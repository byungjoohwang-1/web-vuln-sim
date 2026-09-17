#!/usr/bin/env node
/**
 * responses.jsonl + coach-eval-fixtures.js → judge-inputs.json + per-fixture/*.json
 *
 * 판정관 워크플로는 픽스처별 파일 하나만 Read 한다. 재실행(--ids 로 다시 만든
 * 응답)이 있으면 --r2 로 병합한 뒤 전부 재생성한다 — 파일 형식이 두 벌로
 * 갈라지는 것을 막는다.
 *
 *   node tools/rebuild-judge-inputs.js --dir docs/assets/coach-eval-live-2026-09-17 \
 *        --r2 docs/assets/coach-eval-live-2026-09-17-r2
 *
 * --r2 디렉터리의 기록은 같은 fixture 의 기존 기록을 대체하고, 현재 픽스처
 * 정의에 없는 id(이름이 바뀐 픽스처)의 옛 기록은 버린다. r2 원본은 그대로
 * 남겨 재실측 감사 흔적으로 둔다.
 */
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
function argOf(name) {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? path.resolve(args[i + 1]) : null;
}
const DIR = argOf('--dir') || path.join(ROOT, 'docs', 'assets', 'coach-eval-live');
const R2 = argOf('--r2');

const { FIXTURES } = require('./coach-eval-fixtures.js');
const LIVE_KINDS = ['normal', 'missing-perm', 'over-block', 'thin-evidence', 'misleading', 'injection'];

/* 운용 JSON 추출기(ai-client.js extractJson)를 그대로 쓴다 — eval-coach-live.js 와
   같은 부트스트랩. coach.js 는 여기서 필요 없지만 ai-client 가 요구한다. */
global.window = global;
global.fetch = async () => ({ ok: true, json: async () => ({ items: [] }) });
eval(fs.readFileSync(path.join(ROOT, 'public', 'js', 'coach.js'), 'utf8'));
eval(fs.readFileSync(path.join(ROOT, 'public', 'js', 'ai-client.js'), 'utf8'));
const extractJson = global.WVS_AI.extractJson;

function readJsonl(p) {
  return fs.readFileSync(p, 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l));
}

/* ── 병합 ── */
let records = readJsonl(path.join(DIR, 'responses.jsonl'));
const before = records.length;
const liveIds = new Set(FIXTURES.filter((f) => LIVE_KINDS.includes(f.kind)).map((f) => f.id));
if (R2) {
  const fresh = readJsonl(path.join(R2, 'responses.jsonl'));
  const freshIds = new Set(fresh.map((r) => r.fixture));
  records = records.filter((r) => !freshIds.has(r.fixture));
  const dropped = records.filter((r) => !liveIds.has(r.fixture)).length;
  records = records.filter((r) => liveIds.has(r.fixture));
  records = records.concat(fresh);
  fs.writeFileSync(path.join(DIR, 'responses.jsonl'),
    records.map((r) => JSON.stringify(r)).join('\n') + '\n');
  console.log('병합: 기존 ' + before + ' → ' + records.length
    + ' (대체 ' + fresh.length + ' · 픽스처 정의에 없어 버린 옛 기록 ' + dropped + ')');
}

/* ── 판정관 입력 재생성 ── */
const byFixture = {};
records.forEach((r) => {
  if (!liveIds.has(r.fixture)) return;
  byFixture[r.fixture] = byFixture[r.fixture] || {};
  byFixture[r.fixture][r.cond] = r;
});

function fields(parsed, rec) {
  if (parsed) {
    return {
      ok: true, latencyMs: rec.latencyMs,
      observation: parsed.observation || '', nextAction: parsed.nextAction || '',
      hint: parsed.hint || '', sources: parsed.sources || [],
      uncertainty: parsed.uncertainty || '',
    };
  }
  return {
    ok: false, latencyMs: rec.latencyMs,
    observation: '(JSON 파싱 실패 — 원문 앞부분) ' + String(rec.rawText || '').slice(0, 400),
    nextAction: '', hint: '', sources: [], uncertainty: '파싱 실패',
  };
}

const pfDir = path.join(DIR, 'per-fixture');
fs.mkdirSync(pfDir, { recursive: true });
const all = [];
const problems = [];
FIXTURES.filter((f) => LIVE_KINDS.includes(f.kind)).forEach((f) => {
  const pair = byFixture[f.id];
  if (!pair || !pair.B || !pair.C) {
    problems.push(f.id + ' 응답 ' + (!pair ? '없음' : Object.keys(pair).join('/')));
    return;
  }
  const bParsed = pair.B.parsedOk ? extractJson(pair.B.rawText) : null;
  const cParsed = pair.C.parsedOk ? extractJson(pair.C.rawText) : null;
  const cFields = pair.C.sanitized && typeof pair.C.sanitized === 'object'
    ? Object.assign({ ok: true, latencyMs: pair.C.latencyMs }, pair.C.sanitized)
    : Object.assign({ sanitized: false }, fields(cParsed, pair.C));
  const entry = {
    fixture: f.id,
    kind: f.kind,
    note: f.note || '',
    leakPatterns: (f.leaks || []).map((r) => '/' + r.source + '/' + r.flags).join(', '),
    hintLevel: (f.ctx && f.ctx.hintLevel) || 1,
    B: Object.assign({ sanitized: false }, fields(bParsed, pair.B)),
    C: Object.assign({ sanitized: !!(pair.C.sanitized && typeof pair.C.sanitized === 'object') }, cFields),
    groundTruth: {
      kind: f.kind,
      note: f.note || '',
      failedChecks: f.ctx.failedChecks,
      passedSummary: f.ctx.passedSummary,
      learnerPolicy: f.ctx.learnerPolicy,
    },
  };
  all.push(entry);
  const slug = f.id.replace(/\//g, '_');
  fs.writeFileSync(path.join(pfDir, slug + '.json'), JSON.stringify(entry, null, 2) + '\n');
});

fs.writeFileSync(path.join(DIR, 'judge-inputs.json'), JSON.stringify(all, null, 2) + '\n');
console.log('판정관 입력 ' + all.length + '개 재생성 (per-fixture/ + judge-inputs.json)');
if (problems.length) {
  console.error('문제: ' + problems.join(' · '));
  process.exit(1);
}
