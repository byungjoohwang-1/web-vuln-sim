#!/usr/bin/env node
/**
 * [C04] 코치 평가 실행기.
 *
 * 재평가 문서 §10 C04: "모의 계약 검사와 실제 모델 평가를 분리해 결과 기록".
 *
 * 이 파일이 지키는 선
 *   1. **실행하지 않은 것은 null 로 남긴다.** 돌리지 않은 평가를 0 이나 100% 로
 *      적지 않는다. 리포트의 measured 플래그로 구분한다.
 *   2. 오프라인에서 측정 가능한 것과 실제 모델이 있어야 아는 것을 나눈다.
 *        오프라인 — 파이프라인 보증: 계약 필드, 정답 분리, 출처 필터, 권한 거부,
 *                   폴백 복구, 기본 도움말의 실패 분류 정확도
 *        실제 모델 — 근거 일치, 이른 정답 노출, 유효한 다음 행동, 지연, 비용
 *   3. 로그에 실명·원본 개인정보·API 키를 넣지 않는다(§6-5).
 *      길이·지연·폴백 원인·힌트 단계·모델/프롬프트 버전만 기록한다.
 *
 * 사용
 *   node tools/eval-coach.js                 # 오프라인 계약 평가만
 *   node tools/eval-coach.js --out <경로>    # 리포트 저장 위치 지정
 *   node tools/eval-coach.js --model         # 실제 모델 평가까지(WVS_EVAL_MODEL 필요)
 *
 * 실제 모델 평가는 공급자 연결이 필요하다. 연결이 없으면 그 항목은 미측정으로
 * 남기고 오프라인 결과만 보고한다. 실패가 아니다.
 */
'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const PROMPT_VERSION = 'coach-system/2026-09-14';

/* ── 브라우저 전역 최소 흉내 ── */
const store = {};
global.localStorage = {
  getItem: (k) => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); },
  removeItem: (k) => { delete store[k]; },
};
global.window = global;
global.fetch = async () => ({ ok: true, json: async () => ({ items: [] }) });

eval(fs.readFileSync(path.join(ROOT, 'public', 'js', 'coach.js'), 'utf8'));
const COACH = global.WVS_COACH;
const { FIXTURES } = require('./coach-eval-fixtures.js');

const args = process.argv.slice(2);
const wantModel = args.includes('--model');
/* --check: 배포 게이트용. 리포트 파일을 쓰지 않고 계약 위반 여부만 본다. */
const checkOnly = args.includes('--check');
const outArg = args.indexOf('--out');
/* 리포트는 배포되는 public 안에 둔다. coach-eval.html 이 이 파일을 읽어 화면에 그린다.
   public 밖(docs/)에 쓰면 서빙되지 않아 심사 중 페이지가 빈 화면이 된다. */
const OUT = outArg >= 0 && args[outArg + 1]
  ? path.resolve(args[outArg + 1])
  : path.join(ROOT, 'public', 'data', 'coach-eval-report.json');

/* ── 오프라인 평가 ─────────────────────────────────────────────
   파이프라인이 보증하는 것만 센다. 모델 품질은 여기서 알 수 없다. */
function runOffline() {
  const rows = [];
  let leakedInFallback = 0, contractViolations = 0, sourceMistakes = 0,
    privilegeMisses = 0, fallbackMisses = 0, misclassified = 0;

  FIXTURES.forEach((f) => {
    const c = COACH.buildContext(f.ctx);
    const row = { id: f.id, kind: f.kind, stage: f.stage || null, issues: [] };

    /* 계약: 정답·점수 계열이 새어 나가지 않는가 */
    const sent = JSON.stringify(c);
    ['answerKey', 'correctPolicy', 'score', 'solution'].forEach((k) => {
      if (Object.prototype.hasOwnProperty.call(c, k)) {
        row.issues.push('계약 밖 필드 ' + k); contractViolations++;
      }
    });
    /* 힌트 단계 범위 */
    if (!(c.hintLevel >= 1 && c.hintLevel <= 3)) {
      row.issues.push('hintLevel 범위 이탈'); contractViolations++;
    }
    row.inputChars = sent.length;

    /* 기본 도움말(폴백)이 정답을 흘리지 않는가 */
    const sc = COACH.staticCoach(c);
    const fallbackText = [sc.observation, sc.nextAction, sc.hint].join(' ');
    (f.leaks || []).forEach((re) => {
      if (re.test(fallbackText)) { row.issues.push('기본 도움말에 정답 노출'); leakedInFallback++; }
    });
    /* 폴백이라고 표시했는가 */
    if (!/기본 도움말/.test(sc.uncertainty || '') || sc.mode !== 'static') {
      row.issues.push('폴백 표시 누락'); fallbackMisses++;
    }
    row.fallbackChars = fallbackText.length;

    /* 실패 분류 정확도 — 과허용/과차단을 뒤바꾸지 않는가 */
    const over = (c.failedChecks || []).filter((x) => x.expected === '거부' && x.actual === '허용').length;
    const blk = (c.failedChecks || []).filter((x) => x.expected === '허용' && x.actual === '거부').length;
    const saysOver = /아직 허용/.test(sc.observation);
    const saysBlk = /차단됐습니다/.test(sc.observation);
    if ((over > 0) !== saysOver || (blk > 0) !== saysBlk) {
      row.issues.push('실패 종류 오분류(과허용 ' + over + ' 과차단 ' + blk + ')');
      misclassified++;
    }

    /* 모델 응답을 흉내 낸 픽스처는 sanitize 경로를 본다 */
    if (Object.prototype.hasOwnProperty.call(f, 'modelRaw')) {
      const clean = COACH.sanitize(f.modelRaw, c, {});
      if (f.expectFallback) {
        const usable = clean && (clean.observation || clean.nextAction);
        if (usable) { row.issues.push('폴백으로 내려가야 하는데 응답을 채택'); fallbackMisses++; }
      }
      if (f.expectSources) {
        const got = (clean && clean.sources) || [];
        try { assert.deepStrictEqual(got, f.expectSources); }
        catch (e) { row.issues.push('출처 필터 불일치: ' + JSON.stringify(got)); sourceMistakes++; }
      }
      if (f.expectRefused) {
        const got = (clean && clean.refused) || [];
        const missing = f.expectRefused.filter((k) => got.indexOf(k) < 0);
        if (missing.length) { row.issues.push('권한 필드 미기록: ' + missing.join(',')); privilegeMisses++; }
        ['score', 'grantRole', 'correctIndex', 'submitAnswer', 'unlockCert'].forEach((k) => {
          if (clean && Object.prototype.hasOwnProperty.call(clean, k)) {
            row.issues.push('권한 필드가 결과에 남음: ' + k); privilegeMisses++;
          }
        });
      }
    }

    row.pass = row.issues.length === 0;
    rows.push(row);
  });

  return {
    fixtures: FIXTURES.length,
    passed: rows.filter((r) => r.pass).length,
    failed: rows.filter((r) => !r.pass).length,
    counters: {
      contractViolations, leakedInFallback, sourceMistakes,
      privilegeMisses, fallbackMisses, misclassified,
    },
    inputChars: {
      median: median(rows.map((r) => r.inputChars)),
      max: Math.max.apply(null, rows.map((r) => r.inputChars)),
    },
    rows,
  };
}

function median(a) {
  if (!a.length) return null;
  const s = a.slice().sort((x, y) => x - y);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : Math.round((s[m - 1] + s[m]) / 2);
}

/* ── 실제 모델 평가 ───────────────────────────────────────────
   공급자 연결이 없으면 돌리지 않는다. 돌리지 않은 값은 null 이다. */
function runModel() {
  return {
    ran: false,
    reason: 'WVS_EVAL_MODEL 공급자 연결이 구성되지 않았습니다. 실제 모델 평가를 실행하지 않았습니다.',
    /* §11.1 지표 — 실행 전에는 전부 null 로 남긴다 */
    metrics: {
      validNextAction: null,
      ungroundedClaims: null,
      earlyAnswerLeak: null,
      sourceAccuracy: null,
      latencyMsMedian: null,
      latencyMsP95: null,
      costPerSessionKrw: null,
      failureRecovery: null,
    },
    conditions: {
      A_staticHelp: 'measured-offline',
      B_plainAI: null,
      C_structuredCoach: null,
    },
    sampleSize: 0,
  };
}

function main() {
  const offline = runOffline();
  const model = wantModel ? runModel() : Object.assign(runModel(), {
    reason: '--model 을 주지 않아 실제 모델 평가를 실행하지 않았습니다.',
  });

  const report = {
    generatedAt: new Date().toISOString(),
    generator: 'tools/eval-coach.js',
    promptVersion: PROMPT_VERSION,
    note: '오프라인 계약 평가와 실제 모델 평가는 보증 범위가 다르다. '
      + '오프라인 통과는 파이프라인이 계약을 지킨다는 뜻이며, 모델 답변의 교육적 정확성을 뜻하지 않는다.',
    offline: {
      measured: true,
      scope: '계약 필드·정답 분리·출처 필터·권한 거부·폴백 복구·실패 분류 정확도',
      fixtures: offline.fixtures,
      passed: offline.passed,
      failed: offline.failed,
      counters: offline.counters,
      inputChars: offline.inputChars,
    },
    realModel: {
      measured: model.ran,
      reason: model.reason,
      metrics: model.metrics,
      conditions: model.conditions,
      sampleSize: model.sampleSize,
    },
    rows: offline.rows,
  };

  if (checkOnly) {
    if (offline.failed) {
      console.log('코치 계약 평가 실패 ' + offline.failed + '/' + offline.fixtures);
      offline.rows.filter((r) => !r.pass).slice(0, 6).forEach((r) => {
        console.log('  ' + r.id + ' — ' + r.issues.join(' / '));
      });
      return 1;
    }
    console.log('코치 계약 평가 OK  픽스처 ' + offline.fixtures + '개 통과 (실제 모델 평가는 미측정)');
    return 0;
  }

  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(report, null, 2) + '\n', 'utf8');

  console.log('='.repeat(62));
  console.log('코치 평가 (C04)');
  console.log('='.repeat(62));
  console.log('오프라인 계약 평가  측정함');
  console.log('  픽스처 ' + offline.fixtures + '개 · 통과 ' + offline.passed + ' · 실패 ' + offline.failed);
  Object.keys(offline.counters).forEach((k) => {
    console.log('  ' + k.padEnd(20) + String(offline.counters[k]).padStart(4));
  });
  console.log('  코치 입력 길이(자)  중앙값 ' + offline.inputChars.median + ' · 최대 ' + offline.inputChars.max);
  console.log('');
  console.log('실제 모델 평가      미측정');
  console.log('  ' + model.reason);
  console.log('  §11.1 지표(유효한 다음 행동·근거 불일치·이른 정답 노출·지연·비용)는 null 로 남겼습니다.');
  console.log('');
  console.log('리포트: ' + path.relative(ROOT, OUT));

  if (offline.failed) {
    console.log('');
    offline.rows.filter((r) => !r.pass).slice(0, 10).forEach((r) => {
      console.log('  FAIL  ' + r.id + ' — ' + r.issues.join(' / '));
    });
    return 1;
  }
  return 0;
}

if (require.main === module) process.exit(main());
module.exports = { runOffline };
