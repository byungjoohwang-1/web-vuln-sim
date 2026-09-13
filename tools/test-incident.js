#!/usr/bin/env node
/**
 * [G08] 대표 사건 고정 검사기 테스트.
 *
 * 가장 중요한 확인 (재평가 문서 R-05):
 *   "전부 거부"가 만점이 되면 안 된다. 정상 동작 유지와 비인가 차단을 함께 봐야 한다.
 *   한쪽만 검사하면 학습자가 서비스를 죽이고 합격하는 법을 배운다.
 *
 * 실행: node tools/test-incident.js
 */
'use strict';
const assert = require('assert');
const INC = require('../public/js/incident-engine.js');

let pass = 0;
const ok = (n) => { console.log('  PASS  ' + n); pass++; };

/* ── 1단계: 인가 정책 ── */

/* 올바른 정책: 본인이거나 admin */
const GOOD_S1 = { join: 'or', conds: [
  { left: 'req.userId', op: '==', right: 'vehicle.ownerId' },
  { left: 'req.role', op: '==', right: "'admin'" },
]};
let g = INC.grade('api-authz', GOOD_S1);
assert.strictEqual(g.passed, true, '올바른 정책은 통과해야 함: ' + g.message);
assert.strictEqual(g.keepsWorking, true);
assert.strictEqual(g.blocksAbuse, true);
ok('1단계 — 올바른 인가 정책(본인 또는 admin)이 통과');

/* 전부 허용 = 원래 취약 상태 */
const ALLOW_ALL = { join: 'and', conds: [{ left: 'true', op: '==', right: 'true' }] };
g = INC.grade('api-authz', ALLOW_ALL);
assert.strictEqual(g.passed, false, '전부 허용이 통과하면 안 됨');
assert.strictEqual(g.keepsWorking, true, '정상 동작은 되지만');
assert.strictEqual(g.blocksAbuse, false, '비인가를 못 막는다');
assert.ok(/비인가 동작이 아직 허용/.test(g.message), '실패 이유가 조건으로 설명돼야 함: ' + g.message);
ok('1단계 — 전부 허용은 실패 + 이유가 "비인가가 아직 허용됨"');

/* [R-05 핵심] 전부 거부 — 비인가는 100% 막히지만 서비스가 죽는다 */
const DENY_ALL = { join: 'and', conds: [{ left: 'req.userId', op: '!=', right: 'req.userId' }] };
g = INC.grade('api-authz', DENY_ALL);
assert.strictEqual(g.blocksAbuse, true, '전부 거부면 비인가는 막힌다');
assert.strictEqual(g.keepsWorking, false, '그러나 정상 사용자도 막힌다');
assert.strictEqual(g.passed, false, '전부 거부가 통과하면 안 됨 — 이게 R-05 의 핵심');
assert.ok(/정상 사용자까지 차단/.test(g.message), '실패 이유 설명: ' + g.message);
ok('1단계 — 전부 거부는 실패 (R-05: 서비스를 죽이고 합격할 수 없다)');

/* 빈 정책(기본 거부)도 마찬가지로 실패 */
g = INC.grade('api-authz', { join: 'and', conds: [] });
assert.strictEqual(g.passed, false, '빈 정책도 실패');
assert.strictEqual(g.keepsWorking, false);
ok('1단계 — 빈 정책(기본 거부)도 실패');

/* 소유자만 확인하고 admin 을 빠뜨린 경우 — 정상 1건이 막힌다 */
const NO_ADMIN = { join: 'and', conds: [{ left: 'req.userId', op: '==', right: 'vehicle.ownerId' }] };
g = INC.grade('api-authz', NO_ADMIN);
assert.strictEqual(g.blocksAbuse, true, '비인가는 막힘');
assert.strictEqual(g.keepsWorking, false, 'admin 조회가 막혀 정상 동작이 깨짐');
assert.ok(g.failedTests.includes('s1-admin-read'), '어떤 테스트가 깨졌는지 알려줘야 함');
ok('1단계 — admin 누락 시 실패하고 깨진 테스트를 지목');

/* 역할만 보고 소유를 안 보는 흔한 실수 */
const ROLE_ONLY = { join: 'and', conds: [{ left: 'req.role', op: '!=', right: "'guest'" }] };
g = INC.grade('api-authz', ROLE_ONLY);
assert.strictEqual(g.blocksAbuse, false, '타인 조회가 뚫린다');
assert.ok(g.failedTests.includes('s1-other-read'), '타인 조회 실패를 지목');
ok('1단계 — 역할만 검사하는 실수는 타인 조회로 잡힘');

/* ── 2단계: 업데이트 검증 ── */
g = INC.grade('ota-verify', { signature: true, version: true, target: true });
assert.strictEqual(g.passed, true, '세 검사를 모두 켜면 통과: ' + g.message);
ok('2단계 — 서명·버전·대상 3검사 모두 켜면 통과');

g = INC.grade('ota-verify', { signature: false, version: false, target: false });
assert.strictEqual(g.passed, false, '검사를 끄면 변조본이 통과한다');
assert.strictEqual(g.keepsWorking, true, '정상 패키지는 여전히 설치됨');
assert.strictEqual(g.blocksAbuse, false);
ok('2단계 — 검사를 모두 끄면 변조·되돌리기·오대상이 통과(실패)');

g = INC.grade('ota-verify', { signature: true, version: false, target: true });
assert.strictEqual(g.passed, false, '버전 검사를 빠뜨리면 되돌리기가 통과');
assert.ok(g.failedTests.includes('p-downgrade'), '되돌리기 실패를 지목');
ok('2단계 — 버전 검사 누락 시 되돌리기 공격이 잡힘');

/* 서명만 켜면 대상 불일치가 통과 */
g = INC.grade('ota-verify', { signature: true, version: true, target: false });
assert.ok(g.failedTests.includes('p-wrong-target'), '대상 불일치 실패를 지목');
ok('2단계 — 대상 검사 누락 시 다른 차종용 패키지가 설치됨');

/* ── 3단계: 영향 범위 ── */
const truth = INC.truth();
g = INC.grade('privacy-scope', { affectedVehicles: truth.affectedVehicles, fields: truth.fields });
assert.strictEqual(g.passed, true, '정확히 세면 통과');
ok('3단계 — 영향 범위를 정확히 세면 통과 (차량 ' + truth.affectedVehicles + '대, 항목 ' + truth.fields.join('/') + ')');

g = INC.grade('privacy-scope', { affectedVehicles: 4, fields: truth.fields });
assert.strictEqual(g.passed, false, '정상 접근까지 세면 실패');
ok('3단계 — 정상 접근(ok=true)까지 포함해 세면 실패');

g = INC.grade('privacy-scope', { affectedVehicles: truth.affectedVehicles, fields: ['location'] });
assert.strictEqual(g.passed, false, '항목을 빠뜨리면 실패');
ok('3단계 — 영향 항목을 빠뜨리면 실패');

/* ── 4단계: 전이 ── */
g = INC.grade('transfer', { checkOwner: true });
assert.strictEqual(g.passed, true, '소유 대조를 적용하면 통과');
ok('4단계 — 같은 소유 대조 원리를 적용하면 통과');

g = INC.grade('transfer', { checkOwner: false });
assert.strictEqual(g.passed, false, '적용하지 않으면 실패');
assert.strictEqual(g.keepsWorking, false, '소유 대조가 없으면 이 구현에서는 정상 요청도 허용되지 않는다');
ok('4단계 — 원리를 적용하지 않으면 실패');

/* ── 단계 정의의 정직성 ── */
INC.stages.forEach(function (st) {
  assert.ok(Array.isArray(st.givens) && st.givens.length > 0,
    st.id + ' 단계는 무엇을 가정하는지(givens) 밝혀야 함');
  assert.ok(st.success && st.goal, st.id + ' 는 목표와 성공 조건이 있어야 함');
});
/* 2단계는 "앞 단계가 자동으로 이어지지 않는다"를 명시해야 한다 */
const ota = INC.stages.find((s) => s.id === 'ota-verify');
assert.ok(ota.givens.some((x) => /자동으로 열어 주지는 않는다|별개의 통제/.test(x)),
  '단계 연결을 과장하지 않는다는 설명이 있어야 함');
ok('모든 단계가 가정(givens)과 성공 조건을 명시 · 단계 연결을 과장하지 않음');

assert.strictEqual(INC.isDemoData, true, '합성 데이터임을 표시해야 함');
ok('합성(데모) 데이터 표시');

console.log(`\nALL ${pass} CHECKS PASSED`);
