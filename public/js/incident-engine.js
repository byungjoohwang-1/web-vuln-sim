/**
 * WVS_INCIDENT — 대표 사건 엔진 (G08)
 *
 * 가상의 모빌리티 기업에서 발생한 차량 데이터 접근 사건을 4단계로 다룬다.
 *
 * 설계 원칙 (재평가 문서 §7.1 / R-05):
 *  1) 한 취약점이 자동으로 다음 시스템 침해로 "이어진다"고 말하지 않는다.
 *     각 단계는 앞 단계에서 무엇을 **주어진 것으로 가정하는지**(givens)를 명시한다.
 *  2) 채점은 고정 검사기가 한다. AI 는 채점하지 않는다.
 *  3) 모든 수정 과제는 **정상 동작 유지**와 **비인가 동작 차단**을 함께 본다.
 *     한쪽만 보면 "전부 거부"가 만점이 되어 버린다.
 *  4) 상태 전환 버튼을 누르는 것이 아니라 사용자가 정책을 직접 구성한다.
 *
 * 모든 데이터는 합성(demo)이다. 실제 차량·고객 정보가 아니다.
 */
(function () {
  'use strict';

  /* ── 합성 데이터 ── */
  var VEHICLES = [
    { vin: 'DEMO-VIN-0001', ownerId: 'u-1001', model: 'M3', region: 'KR' },
    { vin: 'DEMO-VIN-0002', ownerId: 'u-1002', model: 'M3', region: 'KR' },
    { vin: 'DEMO-VIN-0003', ownerId: 'u-1003', model: 'X5', region: 'JP' },
  ];

  /* ─────────────────────────────────────────────────────────────
   * 1단계 — API 인가
   * 사용자는 "누가 어떤 차량 자원에 접근할 수 있는가"를 직접 구성한다.
   * 검사기는 6가지 고정 요청으로 정상·비인가를 함께 본다.
   * ───────────────────────────────────────────────────────────── */
  var S1_FIELDS = {
    'req.userId': function (r) { return r.userId; },
    'req.role': function (r) { return r.role; },
    'req.vin': function (r) { return r.vin; },
    'vehicle.ownerId': function (r) { return (byVin(r.vin) || {}).ownerId; },
    'vehicle.region': function (r) { return (byVin(r.vin) || {}).region; },
    "'admin'": function () { return 'admin'; },
    'true': function () { return true; },
  };
  function byVin(vin) {
    for (var i = 0; i < VEHICLES.length; i++) if (VEHICLES[i].vin === vin) return VEHICLES[i];
    return null;
  }

  /** 정책 한 줄 평가. 사용자 코드를 eval 하지 않는다(구조화된 조건만 받는다). */
  function evalCond(cond, req) {
    if (!cond || !cond.left || !cond.op) return false;
    var L = S1_FIELDS[cond.left], R = S1_FIELDS[cond.right];
    if (!L) return false;
    var a = L(req);
    var b = R ? R(req) : cond.right;
    if (cond.op === '==') return a === b;
    if (cond.op === '!=') return a !== b;
    return false;
  }

  /**
   * 정책 = 조건 배열 + 결합 방식.
   * allow 가 true 인 요청만 허용한다(기본 거부).
   */
  function s1Allows(policy, req) {
    if (!policy || !Array.isArray(policy.conds) || !policy.conds.length) return false;
    var results = policy.conds.map(function (c) { return evalCond(c, req); });
    if (policy.join === 'or') return results.some(Boolean);
    return results.every(Boolean);          /* 기본 and */
  }

  /* 고정 시험 요청 — 정상 3 + 비인가 3 */
  var S1_TESTS = [
    { id: 's1-own-read', desc: '차주 u-1001 이 본인 차량 DEMO-VIN-0001 조회',
      req: { userId: 'u-1001', role: 'user', vin: 'DEMO-VIN-0001' }, expect: true, kind: 'normal' },
    { id: 's1-own-read-2', desc: '차주 u-1002 가 본인 차량 DEMO-VIN-0002 조회',
      req: { userId: 'u-1002', role: 'user', vin: 'DEMO-VIN-0002' }, expect: true, kind: 'normal' },
    { id: 's1-admin-read', desc: '점검 담당자(admin) 가 DEMO-VIN-0003 조회',
      req: { userId: 'u-9001', role: 'admin', vin: 'DEMO-VIN-0003' }, expect: true, kind: 'normal' },
    { id: 's1-other-read', desc: '타인 u-1002 가 DEMO-VIN-0001 조회 시도',
      req: { userId: 'u-1002', role: 'user', vin: 'DEMO-VIN-0001' }, expect: false, kind: 'unauthorized' },
    { id: 's1-other-read-2', desc: '타인 u-1003 이 DEMO-VIN-0002 조회 시도',
      req: { userId: 'u-1003', role: 'user', vin: 'DEMO-VIN-0002' }, expect: false, kind: 'unauthorized' },
    { id: 's1-anon-read', desc: '비로그인 요청이 DEMO-VIN-0001 조회 시도',
      req: { userId: null, role: 'guest', vin: 'DEMO-VIN-0001' }, expect: false, kind: 'unauthorized' },
  ];

  /* ─────────────────────────────────────────────────────────────
   * 2단계 — 차량 업데이트 패키지 검증
   * 사용자는 어떤 검사를 켤지 고른다. 검사기는 정상 패키지가 통과하는지도 함께 본다.
   * ───────────────────────────────────────────────────────────── */
  var CURRENT = { version: 7, model: 'M3', region: 'KR' };
  var PKGS = [
    { id: 'p-ok', desc: '정상 패키지 (서명 유효 · v8 · M3/KR 대상)',
      sigValid: true, version: 8, model: 'M3', region: 'KR', expect: true, kind: 'normal' },
    { id: 'p-tampered', desc: '본문이 변조된 패키지 (서명 불일치)',
      sigValid: false, version: 8, model: 'M3', region: 'KR', expect: false, kind: 'unauthorized' },
    { id: 'p-downgrade', desc: '구버전 되돌리기 (v5 · 서명은 유효)',
      sigValid: true, version: 5, model: 'M3', region: 'KR', expect: false, kind: 'unauthorized' },
    { id: 'p-wrong-target', desc: '다른 차종·지역용 패키지 (X5/JP · 서명 유효)',
      sigValid: true, version: 8, model: 'X5', region: 'JP', expect: false, kind: 'unauthorized' },
  ];
  /** checks = {signature:bool, version:bool, target:bool} */
  function s2Accepts(checks, pkg) {
    if (checks.signature && !pkg.sigValid) return false;
    if (checks.version && pkg.version <= CURRENT.version) return false;
    if (checks.target && (pkg.model !== CURRENT.model || pkg.region !== CURRENT.region)) return false;
    return true;
  }

  /* ─────────────────────────────────────────────────────────────
   * 3단계 — 개인정보 영향 범위와 통지 판단
   * 합성 접근 로그에서 "실제로 무엇이 조회됐는지"를 세고, 통지 의무를 판단한다.
   * ───────────────────────────────────────────────────────────── */
  var ACCESS_LOG = [
    { ts: '2026-09-10T01:12:00Z', actor: 'u-1002', vin: 'DEMO-VIN-0001', fields: ['location', 'ownerName'], ok: false },
    { ts: '2026-09-10T01:13:00Z', actor: 'u-1002', vin: 'DEMO-VIN-0003', fields: ['location'], ok: false },
    { ts: '2026-09-10T01:20:00Z', actor: 'u-1001', vin: 'DEMO-VIN-0001', fields: ['location'], ok: true },
    { ts: '2026-09-10T02:02:00Z', actor: 'u-1003', vin: 'DEMO-VIN-0002', fields: ['ownerName', 'phone'], ok: false },
  ];
  /** 정답: 비인가 접근(ok=false)에 등장한 고유 차량 수와 영향받은 정보 항목 */
  function s3Truth() {
    var vins = {}, fields = {};
    ACCESS_LOG.forEach(function (e) {
      if (e.ok) return;
      vins[e.vin] = 1;
      e.fields.forEach(function (f) { fields[f] = 1; });
    });
    return { affectedVehicles: Object.keys(vins).length, fields: Object.keys(fields).sort() };
  }

  /* ─────────────────────────────────────────────────────────────
   * 4단계 — 전이: 같은 인가 원리를 다른 자산에 적용
   * 1단계에서 쓴 "소유 관계를 서버에서 대조한다"를 정비 예약 API 에 적용한다.
   * ───────────────────────────────────────────────────────────── */
  var S4_TESTS = [
    { id: 's4-own', desc: '예약자 본인이 자기 예약 조회', req: { userId: 'u-1001', ownerId: 'u-1001' }, expect: true, kind: 'normal' },
    { id: 's4-other', desc: '다른 사람이 남의 예약 조회', req: { userId: 'u-1002', ownerId: 'u-1001' }, expect: false, kind: 'unauthorized' },
    { id: 's4-anon', desc: '비로그인 요청', req: { userId: null, ownerId: 'u-1001' }, expect: false, kind: 'unauthorized' },
  ];

  /* ─────────────────────────────────────────────────────────────
   * 단계 정의 — givens 로 "무엇을 가정하는지"를 반드시 밝힌다.
   * ───────────────────────────────────────────────────────────── */
  var STAGES = [
    {
      id: 'api-authz',
      title: '1. 차량 조회 API 인가',
      goal: '차주 본인과 점검 담당자만 차량 정보를 볼 수 있게 만든다.',
      givens: ['모든 요청은 이미 로그인 검사를 통과한 뒤 이 지점에 도달한다.',
        '차량-차주 매핑은 신뢰할 수 있는 원장에서 온다.'],
      success: '정상 3건이 모두 허용되고, 비인가 3건이 모두 거부되어야 한다.',
      evidenceIds: ['ev-req-own', 'ev-req-other', 'ev-resp-diff'],
    },
    {
      id: 'ota-verify',
      title: '2. 차량 업데이트 패키지 검증',
      goal: '정상 패키지는 설치되고, 변조·되돌리기·대상 불일치는 거부되게 한다.',
      givens: ['패키지는 이미 단말까지 전달된 상태다. 전송 구간 문제는 이 단계의 대상이 아니다.',
        '서명 검증에 쓸 공개키는 안전하게 배포돼 있다고 본다.',
        '앞 단계(API 인가)의 결과가 이 단계를 자동으로 열어 주지는 않는다. 별개의 통제다.'],
      success: '정상 패키지 1건은 수락, 나머지 3건은 거부되어야 한다.',
      evidenceIds: ['ev-pkg-manifest', 'ev-sig-log'],
    },
    {
      id: 'privacy-scope',
      title: '3. 개인정보 영향 범위 정리',
      goal: '합성 접근 로그에서 비인가 접근의 범위와 영향받은 항목을 정확히 센다.',
      givens: ['로그는 완전하다고 가정한다(누락 없음).',
        '여기서 세는 것은 "무엇이 조회됐는가"이며, 통지 의무의 법적 최종 판단은 별도 검토가 필요하다.'],
      success: '영향 차량 수와 정보 항목 집합이 로그와 일치해야 한다.',
      evidenceIds: ['ev-access-log'],
    },
    {
      id: 'transfer',
      title: '4. 같은 원리를 다른 자산에 적용',
      goal: '1단계에서 쓴 소유 관계 대조를 정비 예약 API 에 그대로 적용한다.',
      givens: ['예약 자원에도 소유자 필드가 있다.',
        '이 단계는 새로운 취약점이 아니라, 배운 원리가 다른 맥락에서도 서는지 확인하는 것이다.'],
      success: '정상 1건 허용, 비인가 2건 거부.',
      evidenceIds: ['ev-booking-schema'],
    },
  ];

  /* ── 채점 (고정 검사기) ── */
  function gradeStage(stageId, answer) {
    var results = [];
    if (stageId === 'api-authz') {
      results = S1_TESTS.map(function (t) {
        var got = s1Allows(answer, t.req);
        return { id: t.id, desc: t.desc, kind: t.kind, expect: t.expect, got: got, pass: got === t.expect };
      });
    } else if (stageId === 'ota-verify') {
      var checks = answer || {};
      results = PKGS.map(function (p) {
        var got = s2Accepts(checks, p);
        return { id: p.id, desc: p.desc, kind: p.kind, expect: p.expect, got: got, pass: got === p.expect };
      });
    } else if (stageId === 'privacy-scope') {
      var truth = s3Truth();
      var a = answer || {};
      var fieldsGiven = (Array.isArray(a.fields) ? a.fields : []).slice().sort();
      results = [
        { id: 's3-count', desc: '비인가 접근이 닿은 차량 수', kind: 'normal',
          expect: truth.affectedVehicles, got: Number(a.affectedVehicles),
          pass: Number(a.affectedVehicles) === truth.affectedVehicles },
        { id: 's3-fields', desc: '영향받은 정보 항목', kind: 'normal',
          expect: truth.fields.join(','), got: fieldsGiven.join(','),
          pass: fieldsGiven.join(',') === truth.fields.join(',') },
      ];
    } else if (stageId === 'transfer') {
      results = S4_TESTS.map(function (t) {
        var got = !!(answer && answer.checkOwner && t.req.userId && t.req.userId === t.req.ownerId);
        return { id: t.id, desc: t.desc, kind: t.kind, expect: t.expect, got: got, pass: got === t.expect };
      });
    }

    var normal = results.filter(function (r) { return r.kind === 'normal'; });
    var unauth = results.filter(function (r) { return r.kind === 'unauthorized'; });
    /* [R-05] 두 축을 함께 봐야 한다. 전부 거부하면 비인가는 100% 막히지만 서비스가 죽는다. */
    var keepsWorking = normal.every(function (r) { return r.pass; });
    var blocksAbuse = unauth.length === 0 || unauth.every(function (r) { return r.pass; });
    return {
      stageId: stageId,
      results: results,
      keepsWorking: keepsWorking,
      blocksAbuse: blocksAbuse,
      passed: keepsWorking && blocksAbuse,
      failedTests: results.filter(function (r) { return !r.pass; }).map(function (r) { return r.id; }),
      /* 실패를 조건으로 설명한다 — "무엇이 아직 허용되는가" */
      message: keepsWorking && blocksAbuse ? '검증 통과'
        : !keepsWorking && !blocksAbuse ? '검증 실패: 정상 동작이 막혔고, 비인가 동작도 아직 허용됩니다.'
          : !keepsWorking ? '검증 실패: 비인가는 막았지만 정상 사용자까지 차단됐습니다.'
            : '검증 실패: 정상 동작은 유지되지만 비인가 동작이 아직 허용됩니다.',
    };
  }

  var API = {
    stages: STAGES,
    vehicles: VEHICLES,
    accessLog: ACCESS_LOG,
    packages: PKGS,
    currentFirmware: CURRENT,
    s1Fields: Object.keys(S1_FIELDS),
    s1Tests: S1_TESTS,
    s4Tests: S4_TESTS,
    truth: s3Truth,
    grade: gradeStage,
    isDemoData: true,
  };
  if (typeof window !== 'undefined') window.WVS_INCIDENT = API;
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
})();
