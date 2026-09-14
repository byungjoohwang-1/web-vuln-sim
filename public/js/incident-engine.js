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
   * 5단계 — 금융 전이 (C06)
   *
   * 왜 별도 과제인가
   *   1단계에서 배운 것은 "요청자와 자원의 소유 관계를 서버에서 대조한다" 다.
   *   그 역량은 그대로 쓰이지만 **전제가 다르다**. 차량은 차주가 한 명이지만
   *   계좌에는 정당한 접근자가 여럿이고(공동명의·법인 담당자), 위임에는
   *   유효 기간이 있다.
   *
   *   그래서 1단계의 "userId == ownerId" 를 그대로 옮기면 공동명의자와
   *   법인 담당자가 막힌다. 반대로 전부 인정하면 만료된 위임이 통과한다.
   *   전이 과제는 "같은 원리, 다른 성공 조건" 을 확인하는 자리다.
   *
   *   통제 원리가 같다고 법적 의무까지 같아지지는 않는다. 이 실습은 접근 통제
   *   구성만 다루며 전자금융거래법상 의무 판단을 대신하지 않는다.
   * ───────────────────────────────────────────────────────────── */
  var FIN_TESTS = [
    { id: 'f-owner', desc: '예금주 본인이 자기 계좌 거래내역 조회',
      req: { userId: 'c-01', isOwner: true }, expect: true, kind: 'normal' },
    { id: 'f-joint', desc: '공동명의자가 같은 계좌 조회',
      req: { userId: 'c-02', isJoint: true }, expect: true, kind: 'normal' },
    { id: 'f-corp', desc: '법인 계좌의 지정 담당자가 자기 법인 계좌 조회',
      req: { userId: 'e-11', isCorpOfficer: true, corpMatch: true }, expect: true, kind: 'normal' },
    { id: 'f-agent-valid', desc: '유효 기간 안의 위임 대리인이 조회',
      req: { userId: 'a-21', isDelegate: true, delegationActive: true }, expect: true, kind: 'normal' },
    { id: 'f-other', desc: '아무 관계 없는 사람이 조회 시도',
      req: { userId: 'c-99' }, expect: false, kind: 'unauthorized' },
    { id: 'f-agent-expired', desc: '위임 기간이 끝난 대리인이 조회 시도',
      req: { userId: 'a-22', isDelegate: true, delegationActive: false }, expect: false, kind: 'unauthorized' },
    { id: 'f-corp-other', desc: '다른 법인의 담당자가 조회 시도',
      req: { userId: 'e-77', isCorpOfficer: true, corpMatch: false }, expect: false, kind: 'unauthorized' },
  ];

  /**
   * 정책 = 어떤 관계를 인정할지 + 위임 기간을 확인할지.
   * 전부 켜는 것이 정답이 아니다. 기간 확인을 빼면 만료된 위임이 통과한다.
   */
  function finAllows(p, r) {
    p = p || {};
    if (p.ownerMatch && r.isOwner) return true;
    if (p.includeJoint && r.isJoint) return true;
    /* 법인 담당자는 "그 계좌의 법인" 인지까지 봐야 한다. */
    if (p.includeCorpOfficer && r.isCorpOfficer && (!p.checkCorpScope || r.corpMatch)) return true;
    if (p.includeDelegate && r.isDelegate && (!p.checkDelegationExpiry || r.delegationActive)) return true;
    return false;
  }

  /* ─────────────────────────────────────────────────────────────
   * 증거 자료 (C01/C02)
   *
   * 예전에는 단계마다 'ev-req-own' 같은 **식별자만** 있었다. 화면에는 그 코드가
   * 그대로 찍혔고, 코치에게도 ID 문자열만 전달됐다. 학습자는 비교할 자료가 없고
   * 모델은 근거 없이 추측하게 된다.
   *
   * 그래서 증거마다 다음을 함께 둔다.
   *   label   — 화면에 보이는 한국어 제목 (내부 ID 는 상세에서만 노출)
   *   summary — 코치에게 보내는 한 줄 의미 (원문 전체를 보내지 않는다)
   *   body    — 학습자가 읽고 비교하는 실제 내용 (합성)
   *
   * 정답(어떤 조건을 써야 하는가)은 여기 담지 않는다. 코치 입력에서 정답을
   * 분리하기 위해서다.
   * ───────────────────────────────────────────────────────────── */
  var EVIDENCE = {
    'ev-req-own': {
      label: '본인 차량 조회 요청과 응답',
      summary: '차주 u-1001 이 자기 차량(DEMO-VIN-0001)을 조회했고 200 으로 성공했다. 이 요청은 계속 허용돼야 하는 정상 동작이다.',
      body: [
        'GET /api/v1/vehicles/DEMO-VIN-0001  HTTP/1.1',
        'Authorization: Bearer <로그인 완료된 세션>',
        '  요청자 userId = u-1001 · role = user',
        '',
        '→ 200 OK',
        '   { "vin": "DEMO-VIN-0001", "ownerId": "u-1001", "location": {...} }',
      ],
    },
    'ev-req-other': {
      label: '타인 차량 조회 요청과 응답',
      summary: '다른 사용자 u-1002 가 u-1001 의 차량(DEMO-VIN-0001)을 조회했는데 같은 200 으로 성공했다. 이 요청은 거부돼야 한다.',
      body: [
        'GET /api/v1/vehicles/DEMO-VIN-0001  HTTP/1.1',
        'Authorization: Bearer <로그인 완료된 세션>',
        '  요청자 userId = u-1002 · role = user',
        '',
        '→ 200 OK   ← 본인 요청과 응답이 같다',
        '   { "vin": "DEMO-VIN-0001", "ownerId": "u-1001", "location": {...} }',
      ],
    },
    'ev-resp-diff': {
      label: '두 응답의 차이 대조',
      summary: '두 요청은 요청자만 다르고 응답은 동일하다. 즉 현재 경로는 로그인 여부만 보고 자원의 소유 관계를 보지 않는다.',
      body: [
        '            본인 요청(u-1001)      타인 요청(u-1002)',
        '  상태코드   200                    200',
        '  본문       차량 전체 정보          차량 전체 정보',
        '  차이       없음                    없음',
        '',
        '  * 응답에 담긴 ownerId 는 u-1001 로 동일하다.',
      ],
    },
    'ev-pkg-manifest': {
      label: '업데이트 패키지 목록',
      summary: '네 개의 패키지가 있다. 서명 유효 여부, 버전(현재 v7), 대상 차종·지역이 서로 다르다.',
      body: [
        '현재 차량: 버전 v7 · 차종 M3 · 지역 KR',
        '',
        '  p-ok            서명 유효   v8   M3/KR',
        '  p-tampered      서명 불일치 v8   M3/KR',
        '  p-downgrade     서명 유효   v5   M3/KR',
        '  p-wrong-target  서명 유효   v8   X5/JP',
      ],
    },
    'ev-sig-log': {
      label: '서명 검증 로그',
      summary: '변조 패키지에서만 서명 해시가 어긋난다. 되돌리기와 대상 불일치 패키지는 서명 자체는 정상이라 서명 검사만으로는 걸러지지 않는다.',
      body: [
        'p-ok           signature=OK    digest 일치',
        'p-tampered     signature=FAIL  digest 불일치 (본문 변조)',
        'p-downgrade    signature=OK    digest 일치',
        'p-wrong-target signature=OK    digest 일치',
        '',
        '* 서명이 유효하다는 것은 "누가 만들었는지"만 말해 준다.',
        '  그 패키지를 지금 이 차량에 설치해도 되는지는 말해 주지 않는다.',
      ],
    },
    'ev-access-log': {
      label: '차량 데이터 접근 로그',
      summary: '접근 4건 중 3건이 비인가(ok=false)다. 비인가 접근이 닿은 차량과 조회된 정보 항목을 세는 것이 이 단계의 과제다.',
      body: ACCESS_LOG.map(function (e) {
        return (e.ok ? '  정상  ' : '  비인가 ') + e.ts + '  actor=' + e.actor +
          '  vin=' + e.vin + '  조회항목=[' + e.fields.join(', ') + ']';
      }),
    },
    'ev-fin-account': {
      label: '계좌에 연결된 사람들',
      summary: '계좌 하나에 정당한 접근자가 여럿이다. 예금주 1명, 공동명의자 1명, 법인 계좌의 지정 담당자, 기간이 정해진 위임 대리인이 있다.',
      body: [
        '계좌 ACC-4410 (개인) — 예금주 c-01 · 공동명의자 c-02',
        '계좌 ACC-8890 (법인) — 지정 담당자 e-11 (소속 법인 일치)',
        '',
        '위임 등록부',
        '  a-21  대상 ACC-4410  기간 2026-09-01 ~ 2026-12-31   상태 유효',
        '  a-22  대상 ACC-4410  기간 2026-01-01 ~ 2026-06-30   상태 만료',
        '',
        '* 차량은 차주가 한 명이었지만, 계좌는 그렇지 않다.',
      ],
    },
    'ev-fin-attempts': {
      label: '조회 시도 기록',
      summary: '7건의 조회 시도 중 4건은 정당하고 3건은 막혀야 한다. 만료된 위임과 다른 법인 담당자가 섞여 있다.',
      body: FIN_TESTS.map(function (t) {
        return (t.kind === 'normal' ? '  허용돼야 함  ' : '  거부돼야 함  ') + t.desc;
      }),
    },
    'ev-booking-schema': {
      label: '정비 예약 자원 구조',
      summary: '예약 자원에도 소유자 필드(ownerId)가 있다. 차량과 자원 종류는 다르지만 소유 관계를 대조한다는 점은 같다.',
      body: [
        'GET /api/v1/bookings/{bookingId}',
        '',
        '예약 자원:',
        '  { "bookingId": "BK-7781", "ownerId": "u-1001",',
        '    "vin": "DEMO-VIN-0001", "slot": "2026-09-20T10:00Z" }',
        '',
        '* 요청자 userId 와 예약의 ownerId 가 비교 대상이다.',
      ],
    },
  };

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
    {
      id: 'finance-transfer',
      title: '5. 다른 분야에서 다시 풀기 — 금융 거래 조회',
      goal: '계좌 거래내역을 조회할 수 있는 사람을 정한다. 정당한 접근자는 모두 통과시키고 그 밖은 막는다.',
      givens: ['모든 요청은 이미 로그인 검사를 통과했다.',
        '앞 단계와 같은 역량(소유·업무 권한 대조)을 쓰지만 전제가 다르다. ' +
        '계좌에는 정당한 접근자가 여럿이고, 위임에는 기간이 있다.',
        '이 실습은 접근 통제 구성만 다룬다. 전자금융거래법상 의무 판단을 대신하지 않는다.'],
      success: '정상 4건(예금주·공동명의자·법인 담당자·유효 위임)이 모두 허용되고, '
        + '비인가 3건(타인·만료 위임·다른 법인 담당자)이 모두 거부되어야 한다.',
      evidenceIds: ['ev-fin-account', 'ev-fin-attempts'],
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
    } else if (stageId === 'finance-transfer') {
      results = FIN_TESTS.map(function (t) {
        var got = finAllows(answer, t.req);
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

  /**
   * 검사 결과 한 건이 "무슨 뜻인지" 한국어로 만든다 (C02).
   * 화면과 코치 입력이 같은 문장을 쓰도록 엔진에 둔다. 두 곳에서 따로 쓰면
   * 학습자가 보는 설명과 모델이 받는 설명이 갈라진다.
   * 정답(어떤 조건을 써야 하는가)은 말하지 않는다. 관찰된 사실만 적는다.
   */
  function explainResult(r) {
    if (!r) return '';
    if (r.pass) {
      return r.kind === 'unauthorized'
        ? '비인가 요청이 의도대로 거부됐다.'
        : '정상 요청이 의도대로 허용됐다.';
    }
    if (r.kind === 'unauthorized') return '거부돼야 하는 요청이 아직 허용된다.';
    if (typeof r.expect === 'boolean') return '허용돼야 하는 정상 요청이 차단됐다.';
    /* 3단계처럼 값 비교인 경우 */
    return '입력한 값(' + r.got + ')이 로그에서 센 값과 다르다.';
  }

  /** 증거 한 건을 돌려준다. 없으면 null. */
  function evidence(id) {
    var e = EVIDENCE[id];
    if (!e) return null;
    return { id: id, label: e.label, summary: e.summary, body: e.body.slice() };
  }

  var API = {
    stages: STAGES,
    evidence: evidence,
    evidenceIds: Object.keys(EVIDENCE),
    explainResult: explainResult,
    vehicles: VEHICLES,
    accessLog: ACCESS_LOG,
    packages: PKGS,
    currentFirmware: CURRENT,
    s1Fields: Object.keys(S1_FIELDS),
    s1Tests: S1_TESTS,
    s4Tests: S4_TESTS,
    finTests: FIN_TESTS,
    truth: s3Truth,
    grade: gradeStage,
    isDemoData: true,
  };
  if (typeof window !== 'undefined') window.WVS_INCIDENT = API;
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
})();
