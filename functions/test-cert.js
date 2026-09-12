/**
 * cert.js 검증 테스트 (네트워크·에뮬레이터 없이 실행 가능).
 *   node functions/test-cert.js
 * 확인 항목:
 *  1) 응시자에게 내려가는 문항에 정답(a)·해설(e)이 포함되지 않는다.
 *  2) 오답 제출은 불합격이며, 문항별 정답이 노출되지 않는다.
 *  3) 정답 제출은 합격하고 서버가 서명된 수료증을 발급한다.
 *  4) 발급된 수료증의 내용을 조작하면 서명 검증이 실패한다.
 *  5) 응시 세션(sid)의 uid를 바꿔치기하면 거부된다.
 *  6) 서명이 손상된 sid는 거부된다.
 *  7) 하루 응시 횟수 제한이 동작한다.
 */
const assert = require("assert");
const crypto = require("crypto");
const { BANK, byId } = require("./exam-bank");
const cert = require("./cert");

/* ── 최소 Firestore 모의 ── */
function makeDb() {
  const store = new Map();
  const key = (c, d) => `${c}/${d}`;
  return {
    _store: store,
    collection(c) {
      return {
        doc(d) {
          const k = key(c, d);
          return {
            async get() {
              const v = store.get(k);
              return { exists: v !== undefined, data: () => v };
            },
            async set(val, opt) {
              const cur = store.get(k);
              store.set(k, opt && opt.merge && cur ? { ...cur, ...val } : val);
            },
          };
        },
      };
    },
  };
}

function b64urlDecode(s) {
  s = String(s).replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  return Buffer.from(s, "base64").toString("utf8");
}
function b64urlEncode(o) {
  return Buffer.from(JSON.stringify(o)).toString("base64")
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

let pass = 0;
function ok(name) { console.log("  PASS  " + name); pass++; }

(async () => {
  const db = makeDb();
  const UID = "user-abc";

  /* 1) 문항 배부에 정답이 없어야 한다 */
  const start = await cert.handleStart(db, UID);
  assert.strictEqual(start.status, 200, "start 200");
  const { sid, questions, total } = start.body;
  assert.ok(Array.isArray(questions) && questions.length === total && total > 0, "questions present");
  const leaked = questions.filter((q) => "a" in q || "e" in q);
  assert.strictEqual(leaked.length, 0, "정답/해설이 클라이언트로 유출되면 안 됨");
  const serialized = JSON.stringify(start.body);
  // 은행의 해설 문장이 응답에 포함되면 유출
  const anyExplanation = BANK.some((b) => serialized.includes(b.e));
  assert.strictEqual(anyExplanation, false, "해설 문자열 유출 없음");
  ok("배부 문항에 정답·해설 미포함");

  /* sid 에서 문항 순서 추출(테스트 목적) */
  const raw = sid.slice(0, sid.lastIndexOf("."));
  const payload = JSON.parse(b64urlDecode(raw));
  const ids = payload.ids;

  /* 2) 오답 제출 → 불합격 + 정답 미노출 */
  const wrong = ids.map((qid) => (byId(qid).a === 0 ? 1 : 0));
  const failRes = await cert.handleSubmit(db, UID, { sid, answers: wrong, name: "테스터" });
  assert.strictEqual(failRes.status, 200);
  assert.strictEqual(failRes.body.pass, false, "오답은 불합격");
  assert.ok(!("review" in failRes.body), "불합격 시 문항별 리뷰 미제공");
  assert.ok(!JSON.stringify(failRes.body).includes("correctIndex"), "정답 인덱스 미노출");
  ok("오답 제출 → 불합격, 정답 비공개");

  /* 3) 정답 제출 → 합격 + 서명된 수료증 발급 */
  const start2 = await cert.handleStart(db, UID);
  const sid2 = start2.body.sid;
  const ids2 = JSON.parse(b64urlDecode(sid2.slice(0, sid2.lastIndexOf(".")))).ids;
  const right = ids2.map((qid) => byId(qid).a);
  const passRes = await cert.handleSubmit(db, UID, { sid: sid2, answers: right, name: "홍길동" });
  assert.strictEqual(passRes.body.pass, true, "정답은 합격");
  assert.strictEqual(passRes.body.score, 100);
  const certId = passRes.body.certId;
  assert.ok(/^WVS-VC-\d{4}-[0-9A-F]{8}$/.test(certId), "certId 형식");
  ok("정답 제출 → 합격, 서명 수료증 발급 " + certId);

  /* 서버 검증이 유효하다고 판정 */
  const v1 = await cert.handleVerify(db, certId);
  assert.strictEqual(v1.body.found, true);
  assert.strictEqual(v1.body.verified, true, "정상 수료증은 verified=true");
  ok("발급 직후 서버 검증 통과");

  /* 4) 저장된 수료증 내용 조작 → 서명 불일치 */
  const stored = db._store.get(`certificates/${certId}`);
  db._store.set(`certificates/${certId}`, { ...stored, score: 100, correct: stored.total, name: "위조자" });
  const v2 = await cert.handleVerify(db, certId);
  assert.strictEqual(v2.body.verified, false, "이름 변조 시 서명 실패해야 함");
  ok("수료증 변조 → 서명 검증 실패(위조 탐지)");
  db._store.set(`certificates/${certId}`, stored); // 복구

  /* 5) sid 의 uid 바꿔치기 → 거부 */
  const start3 = await cert.handleStart(db, UID);
  const sid3 = start3.body.sid;
  const raw3 = sid3.slice(0, sid3.lastIndexOf("."));
  const sig3 = sid3.slice(sid3.lastIndexOf(".") + 1);
  const p3 = JSON.parse(b64urlDecode(raw3));
  p3.uid = "attacker";
  const forged = `${b64urlEncode(p3)}.${sig3}`;             // 서명은 그대로 재사용
  const r5 = await cert.handleSubmit(db, "attacker", { sid: forged, answers: p3.ids.map(() => 0) });
  assert.strictEqual(r5.status, 400, "서명 불일치로 거부");
  assert.ok(/위조/.test(r5.body.error), "위조 감지 메시지");
  ok("sid uid 위조 → 거부");

  /* 6) 다른 사용자가 남의 sid 재사용 → 거부 */
  const r6 = await cert.handleSubmit(db, "someone-else", { sid: sid3, answers: p3.ids.map(() => 0) });
  assert.strictEqual(r6.status, 403, "sid 소유자 불일치 거부");
  ok("타인 sid 재사용 → 403 거부");

  /* 7) 하루 응시 횟수 제한 */
  const db2 = makeDb();
  const U2 = "limited-user";
  let last;
  for (let i = 0; i < cert.MAX_ATTEMPTS_PER_DAY + 1; i++) last = await cert.handleStart(db2, U2);
  assert.strictEqual(last.status, 429, "초과 시 429");
  ok(`하루 응시 제한(${cert.MAX_ATTEMPTS_PER_DAY}회) 동작`);

  console.log(`\nALL ${pass} CHECKS PASSED`);
})().catch((e) => {
  console.error("\nFAILED:", e && e.message);
  console.error(e);
  process.exit(1);
});
