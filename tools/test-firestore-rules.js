#!/usr/bin/env node
/**
 * firestore.rules 보안 회귀 테스트 (QA-P0-05 완료 기준).
 *   firebase emulators:exec --only firestore "node tools/test-firestore-rules.js"
 *
 * 핵심 검증: 로그인한 사용자가 브라우저에서 "임의 점수/수료증"을 직접 기록할 수 없어야 한다.
 * 에뮬레이터 REST API + 에뮬레이터가 신뢰하는 비서명 JWT 로 실제 규칙을 그대로 평가한다
 * (추가 npm 의존성 없이 배포될 규칙 파일 자체를 검사).
 */
const PROJECT = process.env.GCLOUD_PROJECT || process.env.FIREBASE_PROJECT || 'vuln-sim';
const HOST = process.env.FIRESTORE_EMULATOR_HOST || '127.0.0.1:8080';
const BASE = `http://${HOST}/v1/projects/${PROJECT}/databases/(default)/documents`;

function b64url(o) {
  return Buffer.from(JSON.stringify(o)).toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
/** 에뮬레이터는 서명을 검증하지 않는다. uid 클레임만 있으면 인증 사용자로 평가한다. */
function tokenFor(uid) {
  const header = b64url({ alg: 'none', typ: 'JWT' });
  const now = Math.floor(Date.now() / 1000);
  const payload = b64url({
    iss: `https://securetoken.google.com/${PROJECT}`, aud: PROJECT,
    auth_time: now, user_id: uid, sub: uid, iat: now, exp: now + 3600,
    firebase: { identities: {}, sign_in_provider: 'custom' },
  });
  return `${header}.${payload}.`;
}

async function req(method, path, { uid, fields } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (uid) headers.Authorization = `Bearer ${tokenFor(uid)}`;
  const res = await fetch(`${BASE}/${path}`, {
    method, headers,
    body: fields ? JSON.stringify({ fields }) : undefined,
  });
  return { status: res.status, body: await res.text() };
}

const S = (v) => ({ stringValue: String(v) });
const I = (v) => ({ integerValue: String(v) });

let pass = 0, fail = 0;
function check(name, cond, detail) {
  if (cond) { console.log('  PASS  ' + name); pass++; }
  else { console.log('  FAIL  ' + name + (detail ? '  → ' + detail : '')); fail++; }
}
const denied = (r) => r.status === 403 || r.status === 401;

(async () => {
  const UID = 'attacker-uid';
  console.log(`rules test against ${BASE}\n`);

  // 1) 수료증 위조 생성 시도 — 반드시 거부
  let r = await req('PATCH', 'certificates/FORGED-001', {
    uid: UID, fields: { uid: S(UID), name: S('위조자'), score: I(100), certId: S('FORGED-001'), kind: S('verified') },
  });
  check('클라이언트의 certificates 생성 거부', denied(r), `status=${r.status}`);

  // 2) 서버 발급본 변조 시도 — 반드시 거부
  r = await req('PATCH', 'certificates/WVS-VC-2026-AAAABBBB', {
    uid: UID, fields: { score: I(100) },
  });
  check('클라이언트의 certificates 수정 거부', denied(r), `status=${r.status}`);

  // 3) 리더보드 점수 위조 — 반드시 거부(본인 문서라도)
  r = await req('PATCH', `leaderboard/${UID}`, {
    uid: UID, fields: { name: S('위조자'), score: I(9999), xp: I(999999), verified: { booleanValue: true } },
  });
  check('본인 leaderboard 문서 쓰기도 거부(점수 위조 차단)', denied(r), `status=${r.status}`);

  // 4) 응시 횟수 카운터 조작 — 반드시 거부
  r = await req('PATCH', `certAttempts/${UID}_2026-09-12`, { uid: UID, fields: { n: I(0) } });
  check('certAttempts 조작 거부', denied(r), `status=${r.status}`);
  r = await req('GET', `certAttempts/${UID}_2026-09-12`, { uid: UID });
  check('certAttempts 읽기 거부', denied(r), `status=${r.status}`);

  // 4-b) [G01] 응시 세션 — 읽으면 문항이 새고, 쓰면 status 를 되돌려 재응시할 수 있다
  r = await req('GET', 'certSessions/abc123', { uid: UID });
  check('certSessions 읽기 거부(문항 유출 차단)', denied(r), `status=${r.status}`);
  r = await req('PATCH', 'certSessions/abc123', { uid: UID, fields: { status: S('open') } });
  check('certSessions 쓰기 거부(세션 재개봉 차단)', denied(r), `status=${r.status}`);

  // 5) 자가 기록(selfCerts)은 본인 uid + kind:'self' 로만 생성 가능
  r = await req('PATCH', 'selfCerts/SELF-001', {
    uid: UID, fields: { uid: S(UID), kind: S('self'), name: S('학습자'), certId: S('SELF-001'), score: I(80) },
  });
  check('selfCerts 자가 기록 생성 허용', r.status === 200, `status=${r.status}`);

  r = await req('PATCH', 'selfCerts/SELF-002', {
    uid: UID, fields: { uid: S('someone-else'), kind: S('self'), certId: S('SELF-002') },
  });
  check('selfCerts 타인 uid 로 생성 거부', denied(r), `status=${r.status}`);

  r = await req('PATCH', 'selfCerts/SELF-003', {
    uid: UID, fields: { uid: S(UID), kind: S('verified'), certId: S('SELF-003') },
  });
  check("selfCerts 에 kind:'verified' 위장 거부", denied(r), `status=${r.status}`);

  // 6) [QA N-04] 수료증 문서에는 실명이 들어 있다. 예전에는 제3자 검증 경로를 위해
  //    무인증 단건 조회를 열어 뒀지만, 수료번호를 훑어 이름을 모을 수 있었다.
  //    공개 검증은 certApi(action=verify)가 이름을 가려서 내려주므로 직접 조회는 막는다.
  r = await req('GET', 'certificates/ANY-ID');
  check('비로그인 수료증 직접 조회 거부(실명 수집 차단)', denied(r), `status=${r.status}`);

  r = await req('GET', 'certificates/ANY-ID', { uid: UID });
  check('로그인해도 수료증 직접 조회 거부', denied(r), `status=${r.status}`);

  // 7) 클래스 목록 훑기 차단(참여는 코드를 아는 사람이 단건으로)
  r = await req('GET', 'classes', { uid: UID });
  check('classes 목록 열람 거부', denied(r), `status=${r.status}`);

  // 7) 리더보드 읽기는 로그인 사용자에게 허용
  r = await req('GET', 'leaderboard/someone', { uid: UID });
  check('로그인 사용자의 leaderboard 읽기 허용', !denied(r), `status=${r.status}`);

  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})().catch((e) => { console.error('test error', e); process.exit(1); });
