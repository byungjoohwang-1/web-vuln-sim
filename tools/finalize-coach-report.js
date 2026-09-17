#!/usr/bin/env node
/**
 * [P0-1 마무리] final-synth 워크플로 결과 + 실측 통계 → coach-eval-report.json realModel 블록.
 *
 * realModel 은 eval-coach.js 가 못 만든다(실행기가 분리돼 있으므로). 이 스크립트가
 * 판정 병합·집계가 끝난 최종 값을 주입한다. 입력이 전부 있어야 실행한다 —
 * 하나라도 비면 미측정 스텁을 그대로 둔다(빈값으로 덮어쓰지 않는다).
 *
 *   node tools/finalize-coach-report.js \
 *     --synth .wf-tmp/final-synth-result.json \
 *     --stats .wf-tmp/live-stats.json \
 *     --summary docs/assets/coach-eval-live-2026-09-17/summary.json
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
const SYNTH = argOf('--synth');
const STATS = argOf('--stats');
const SUMMARY = argOf('--summary');
const OUT = path.join(ROOT, 'public', 'data', 'coach-eval-report.json');
if (!SYNTH || !STATS || !SUMMARY) {
  console.error('--synth --stats --summary 가 모두 필요합니다. realModel 을 그대로 둡니다.');
  process.exit(2);
}
const synth = JSON.parse(fs.readFileSync(SYNTH, 'utf8'));
const stats = JSON.parse(fs.readFileSync(STATS, 'utf8'));
const summary = JSON.parse(fs.readFileSync(SUMMARY, 'utf8'));
const { aggregate: agg, synthesis, critique } = synth;
if (!agg || !synthesis) { console.error('synth 결과에 aggregate/synthesis 가 없습니다.'); process.exit(1); }

const pct = (r) => (r && r.n ? { B: r.B, C: r.C } : null);
const realModel = {
  measured: true,
  reason: '2026-09-17 실측 · 판정 루브릭 v2(교정본)로 28픽스처 전체 재판정 — '
    + '픽스처 결함 3건(상태 미정의 2·라벨 반전 1)과 루브릭 normal 오기를 실측 후 발견·수정하고 '
    + '영향 12종은 재실측·재판정했다.',
  metrics: {
    validNextAction: pct(agg.validNextAction),
    ungroundedClaims: pct(agg.ungroundedClaim),
    earlyAnswerLeak: pct(agg.earlyAnswerLeak),
    sourceAccuracy: null,
    latencyMsMedian: { B: stats.perCond.B.latencyMedian, C: stats.perCond.C.latencyMedian },
    latencyMsP95: { B: stats.perCond.B.latencyP95, C: stats.perCond.C.latencyP95 },
    costPerSessionKrw: null,
    failureRecovery: null,
    injectionResistance: agg.injectionResistance && agg.injectionResistance.n
      ? { B: agg.injectionResistance.B, C: agg.injectionResistance.C } : null,
  },
  conditions: {
    A_staticHelp: 'measured-offline',
    B_plainAI: summary.meta.conditions.B,
    C_structuredCoach: summary.meta.conditions.C,
  },
  sampleSize: '28 픽스처 쌍 · 56 호출 (' + stats.calls + '호출 성공 ' + stats.ok + ' · JSON 파싱 실패 ' + stats.parseFail + ')',
  model: stats.model,
  notes: synthesis.keyFindings.slice(),
  quotes: (synthesis.notableQuotes || []).map((q) => ({ fixture: q.fixture, quote: q.quote, why: q.why })),
  limitations: [
    '유의성 검정 없음 — 1회 측정, 불일치 쌍이 적어 McNemar 로도 유의하지 않음',
    '같은 모델(glm-5.3)이 두 조건의 응답을 생성하고 같은 계열 모델이 판정 — 자기 판정 편향 가능',
    '판정관이 조건 라벨(B/C)을 알고 판정했다',
    '조건 C 입력 토큰이 B 의 약 ' + (stats.perCond.C.tokensInAvg / stats.perCond.B.tokensInAvg).toFixed(1) + '배(평균 '
      + stats.perCond.C.tokensInAvg + ' vs ' + stats.perCond.B.tokensInAvg + ') — 비용 비대칭이 있다',
    '조건 B 질문에는 첫 실패 검사의 기대값/실제값이 포함된다(학습자가 화면에서 볼 수 있는 수준 — 설계 사실)',
    '힌트 수위 1단계 단발만 측정 — 연속 힌트·장기 세션은 미측정',
    '단일 도메인(합성 차량·금융 사고) — 다른 도메인으로의 일반화는 미측정',
    '판정관 간 일치도(inter-rater) 없음 — 판정관 1회 판정',
    'sourceAccuracy·failureRecovery·costPerSessionKrw 는 이번에 측정하지 않았다(null)',
  ],
};
if (critique && critique.missing && critique.missing.length) {
  realModel.limitations = realModel.limitations.concat(critique.missing.map((s) => '[비평가] ' + s));
}

const report = JSON.parse(fs.readFileSync(OUT, 'utf8'));
report.generatedAt = new Date().toISOString();
report.realModel = realModel;
fs.writeFileSync(OUT, JSON.stringify(report, null, 2) + '\n');
console.log('realModel 주입 완료 — sampleSize: ' + realModel.sampleSize);
console.log('validNextAction:', JSON.stringify(realModel.metrics.validNextAction),
  '· leak:', JSON.stringify(realModel.metrics.earlyAnswerLeak),
  '· ungrounded:', JSON.stringify(realModel.metrics.ungroundedClaims),
  '· injection:', JSON.stringify(realModel.metrics.injectionResistance));
console.log('notes ' + realModel.notes.length + '건 · limitations ' + realModel.limitations.length + '건 · quotes ' + realModel.quotes.length + '건');
