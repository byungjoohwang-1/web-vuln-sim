#!/usr/bin/env node
/**
 * [G09] 오개념 복습 엔진 테스트.
 *
 * 가장 중요한 확인:
 *   "오개념"은 학습자 이해에 대한 주장이다. 근거 없이 붙으면 틀린 낙인이 된다.
 *   - 통과한 단계는 근거가 되지 않는다.
 *   - 1회 실패는 'single'(참고용)이지 'observed' 가 아니다.
 *   - 모든 항목이 evidence 를 갖는다(무엇을 보고 그렇게 말했는지).
 *
 * 실행: node tools/test-misconception.js
 */
'use strict';
const assert = require('assert');
const REV = require('../public/js/misconception.js');

let pass = 0;
const ok = (n) => { console.log('  PASS  ' + n); pass++; };

/* ── 1) 통과한 단계는 오개념 근거가 아니다 ── */
let m = REV.collect({
  red: {},
  incident: { 'api-authz': { passed: true, failedTests: [] } },
});
assert.strictEqual(m.length, 0, '통과한 단계에서 오개념이 나오면 안 됨');
ok('통과한 단계는 오개념 근거가 되지 않음');

/* 통과했는데 failedTests 가 남아 있어도(중간 실패 흔적) 무시해야 한다 */
m = REV.collect({
  red: {},
  incident: { 'api-authz': { passed: true, failedTests: ['s1-other-read'] } },
});
assert.strictEqual(m.length, 0, '최종 통과했으면 중간 실패 흔적으로 낙인찍지 않는다');
ok('최종 통과 시 중간 실패 흔적을 오개념으로 삼지 않음');

/* ── 2) 1회 실패는 'single', 2회 이상이라야 'observed' ── */
m = REV.collect({
  red: {},
  incident: { 'api-authz': { passed: false, failedTests: ['s1-other-read'] } },
});
assert.strictEqual(m.length, 1);
assert.strictEqual(m[0].tag, 'authz.ownership');
assert.strictEqual(m[0].confidence, 'single', '1회는 아직 오개념이라 단정하지 않는다');
assert.ok(m[0].evidence.length >= 1, '근거를 남겨야 함');
ok('1회 실패는 single (한 번 틀린 것을 오개념으로 부풀리지 않음)');

m = REV.collect({
  red: {},
  incident: {
    'api-authz': { passed: false, failedTests: ['s1-other-read', 's1-other-read-2'] },
    transfer: { passed: false, failedTests: ['s4-other'] },
  },
});
const own = m.find((x) => x.tag === 'authz.ownership');
assert.ok(own, '소유 관계 오개념이 잡혀야 함');
assert.strictEqual(own.confidence, 'observed', '여러 번 반복되면 observed');
assert.ok(own.count >= 3, '횟수 누적: ' + own.count);
assert.ok(own.evidence.some((e) => /api-authz/.test(e)) && own.evidence.some((e) => /transfer/.test(e)),
  '서로 다른 단계의 근거가 함께 남아야 함(전이 실패를 보여준다)');
ok('같은 오개념이 다른 단계에서 반복되면 observed + 근거 누적');

/* ── 3) 과차단도 오개념으로 잡는다 (R-05 의 반대편) ── */
m = REV.collect({ red: {}, incident: { 'api-authz': { passed: false, failedTests: ['s1-admin-read', 's1-own-read'] } } });
const over = m.find((x) => x.tag === 'authz.overblock');
assert.ok(over, '정상 동작을 막은 것도 오개념으로 다뤄야 함');
assert.strictEqual(over.confidence, 'observed');
assert.ok(/정상 사용까지 차단/.test(over.label), '라벨: ' + over.label);
ok('과차단(정상 동작을 막음)도 오개념으로 기록 — R-05 의 반대편');

/* ── 4) 레드팀 기록: 2회 미만이거나 성공이 더 많으면 제외 ── */
m = REV.collect({ red: { unix: { '계정 관리': { fail: 1, ok: 0 } } }, incident: {} });
assert.strictEqual(m.length, 0, '1회 실패는 레드팀에서도 제외');
m = REV.collect({ red: { unix: { '계정 관리': { fail: 2, ok: 5 } } }, incident: {} });
assert.strictEqual(m.length, 0, '성공이 더 많으면 제외');
m = REV.collect({ red: { unix: { '계정 관리': { fail: 3, ok: 1 } } }, incident: {} });
assert.strictEqual(m.length, 1, '반복 실패 + 성공보다 많음 → 포함');
assert.ok(/3회 실패/.test(m[0].evidence[0]), '근거에 실제 수치: ' + m[0].evidence[0]);
ok('레드팀 기록은 반복 실패 + 성공보다 많을 때만 포함');

/* ── 5) 모든 항목이 근거를 갖는다 ── */
m = REV.collect({
  red: { web: { '인가': { fail: 4, ok: 0 } } },
  incident: { 'ota-verify': { passed: false, failedTests: ['p-downgrade', 'p-tampered'] } },
});
assert.ok(m.length >= 2);
m.forEach((x) => {
  assert.ok(Array.isArray(x.evidence) && x.evidence.length > 0, x.tag + ' 에 근거가 없음');
  assert.ok(x.label && x.why, x.tag + ' 에 설명이 없음');
  assert.ok(['observed', 'single'].includes(x.confidence), x.tag + ' 확신 수준 이상: ' + x.confidence);
});
ok('모든 오개념 항목이 근거·설명·확신 수준을 가짐');

/* ── 6) 복습 제안: 이미 푼 것은 빼고 다른 맥락을 준다 ── */
const ITEMS = [
  { page: '03_code_sql_injection.html', skills: ['CWE-89'], keywords: ['sql'], category: '시큐어코딩 · 구현' },
  { page: 'sim-no-auth.html', skills: ['CWE-306'], keywords: ['인가', '인증'], category: '실습 시뮬레이터' },
  { page: 'sim-idor.html', skills: ['CWE-639'], keywords: ['인가', '권한'], category: '실습 시뮬레이터' },
  { page: '14_auto-auto01.html', skills: [], keywords: ['자동차'], category: '자동차 보안' },
];
const misc = { tag: 'authz.ownership', skills: ['CWE-639', 'CWE-285'] };
let sug = REV.suggest(ITEMS, misc, { limit: 3 });
assert.ok(sug.length >= 1, '제안이 있어야 함');
assert.strictEqual(sug[0].page, 'sim-idor.html', 'CWE 가 맞는 항목이 먼저: ' + sug[0].page);
ok('복습 제안 — 오개념의 기술(CWE)이 맞는 항목을 우선');

sug = REV.suggest(ITEMS, misc, { limit: 3, exclude: { 'sim-idor.html': 1 } });
assert.ok(!sug.some((x) => x.page === 'sim-idor.html'), '이미 푼 항목은 제외');
ok('이미 완료한 항목은 복습 제안에서 제외');

/* 관련 없는 항목은 제안하지 않는다 */
sug = REV.suggest([{ page: 'x.html', skills: [], keywords: ['요리'], category: '기타' }], misc, { limit: 3 });
assert.strictEqual(sug.length, 0, '근거 없는 제안을 만들지 않는다');
ok('관련 근거가 없으면 제안을 만들지 않음');

/* ── 7) 빈 기록이면 아무 주장도 하지 않는다 ── */
m = REV.collect({ red: {}, incident: {} });
assert.strictEqual(m.length, 0, '기록이 없으면 오개념도 없다');
ok('기록이 없으면 아무 주장도 하지 않음');

console.log(`\nALL ${pass} CHECKS PASSED`);
