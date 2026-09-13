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

/* ── 최소 Firestore 모의 ──
 * runTransaction 은 실제 Firestore 처럼 "읽은 문서가 커밋 전에 바뀌면 재시도"하도록 만든다.
 * 이게 없으면 원자성 테스트가 통과해도 아무것도 증명하지 못한다. */
function makeDb() {
  const store = new Map();
  const versions = new Map();               // 문서별 변경 카운터(경합 감지용)
  const key = (c, d) => `${c}/${d}`;
  const bump = (k) => versions.set(k, (versions.get(k) || 0) + 1);
  const write = (k, val, opt) => {
    const cur = store.get(k);
    store.set(k, opt && opt.merge && cur ? { ...cur, ...val } : val);
    bump(k);
  };
  const docRef = (c, d) => ({ _k: key(c, d),
    async get() { const v = store.get(key(c, d)); return { exists: v !== undefined, data: () => v }; },
    async set(val, opt) { write(key(c, d), val, opt); },
  });

  return {
    _store: store,
    collection(c) { return { doc(d) { return docRef(c, d); } }; },
    async runTransaction(fn) {
      for (let attempt = 0; attempt < 8; attempt++) {
        const readVersions = new Map();
        const writes = [];
        const tx = {
          async get(ref) {
            readVersions.set(ref._k, versions.get(ref._k) || 0);
            const v = store.get(ref._k);
            /* 실제 환경처럼 읽기 사이에 다른 트랜잭션이 끼어들 틈을 만든다. */
            await new Promise((r) => setImmediate(r));
            return { exists: v !== undefined, data: () => v };
          },
          set(ref, val, opt) { writes.push([ref._k, val, opt]); },
        };
        const result = await fn(tx);
        /* 커밋 직전 검증: 읽은 문서가 그 사이 바뀌었으면 전부 버리고 재시도 */
        let stale = false;
        for (const [k, v] of readVersions) if ((versions.get(k) || 0) !== v) { stale = true; break; }
        if (stale) continue;
        for (const [k, val, opt] of writes) write(k, val, opt);
        return result;
      }
      throw new Error("transaction: too much contention");
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

  /* ───────── G01: 세션 소비·동시성·버전 고정 ───────── */

  /* 8) 같은 답안 재전송(네트워크 재시도) → 결과 복구, 수료증 1개 */
  const dbA = makeDb();
  const UA = "retry-user";
  const sA = await cert.handleStart(dbA, UA);
  const idsA = JSON.parse(b64urlDecode(sA.body.sid.slice(0, sA.body.sid.lastIndexOf(".")))).ids;
  const rightA = idsA.map((q) => byId(q).a);
  const a1 = await cert.handleSubmit(dbA, UA, { sid: sA.body.sid, answers: rightA, name: "재시도" });
  const a2 = await cert.handleSubmit(dbA, UA, { sid: sA.body.sid, answers: rightA, name: "재시도" });
  assert.strictEqual(a1.body.pass, true);
  assert.strictEqual(a2.status, 200, "동일 답안 재전송은 성공 응답");
  assert.strictEqual(a2.body.certId, a1.body.certId, "같은 수료증이 돌아와야 함");
  assert.strictEqual(a2.body.replayed, true, "재전송임을 표시");
  const certDocs = [...dbA._store.keys()].filter((k) => k.startsWith("certificates/"));
  assert.strictEqual(certDocs.length, 1, "수료증 문서는 1개여야 함 (중복 발급 금지)");
  ok("동일 sid 재전송 → 결과 복구, 수료증 1개");

  /* 9) 불합격 후 답안을 바꿔 재제출 → 거부 */
  const dbB = makeDb();
  const UB = "cheater";
  const sB = await cert.handleStart(dbB, UB);
  const idsB = JSON.parse(b64urlDecode(sB.body.sid.slice(0, sB.body.sid.lastIndexOf(".")))).ids;
  const wrongB = idsB.map((q) => (byId(q).a === 0 ? 1 : 0));
  const b1 = await cert.handleSubmit(dbB, UB, { sid: sB.body.sid, answers: wrongB });
  assert.strictEqual(b1.body.pass, false, "먼저 불합격");
  const b2 = await cert.handleSubmit(dbB, UB, { sid: sB.body.sid, answers: idsB.map((q) => byId(q).a) });
  assert.strictEqual(b2.status, 409, "답안 교체 재제출은 409 거부");
  assert.strictEqual([...dbB._store.keys()].filter((k) => k.startsWith("certificates/")).length, 0, "수료증이 발급되면 안 됨");
  ok("불합격 후 답안 교체 재제출 → 거부(수료증 미발급)");

  /* 10) 동시 제출(같은 sid, 같은 답안) → 결과 1개 */
  const dbC = makeDb();
  const UC = "parallel-user";
  const sC = await cert.handleStart(dbC, UC);
  const idsC = JSON.parse(b64urlDecode(sC.body.sid.slice(0, sC.body.sid.lastIndexOf(".")))).ids;
  const rightC = idsC.map((q) => byId(q).a);
  const par = await Promise.all([1, 2, 3, 4].map(() =>
    cert.handleSubmit(dbC, UC, { sid: sC.body.sid, answers: rightC, name: "동시" })));
  const certIdsC = new Set(par.filter((r) => r.body && r.body.certId).map((r) => r.body.certId));
  assert.strictEqual(certIdsC.size, 1, "동시 제출이어도 수료증 ID는 1개");
  assert.strictEqual([...dbC._store.keys()].filter((k) => k.startsWith("certificates/")).length, 1, "문서도 1개");
  ok("동시 제출 4건 → 수료증 1개");

  /* 11) 동시 응시 시작 → 일일 한도 준수 */
  const dbD = makeDb();
  const UD = "burst-user";
  const bursts = await Promise.all([1, 2, 3, 4, 5, 6].map(() => cert.handleStart(dbD, UD)));
  const okCount = bursts.filter((r) => r.status === 200).length;
  assert.strictEqual(okCount, cert.MAX_ATTEMPTS_PER_DAY,
    `동시 6건 중 ${cert.MAX_ATTEMPTS_PER_DAY}건만 허용돼야 함 (실제 ${okCount})`);
  const day = new Date().toISOString().slice(0, 10);
  assert.strictEqual(dbD._store.get(`certAttempts/${UD}_${day}`).n, cert.MAX_ATTEMPTS_PER_DAY, "카운터도 일치");
  ok(`동시 응시 시작 → 일일 한도(${cert.MAX_ATTEMPTS_PER_DAY}) 준수`);

  /* 12) 만료된 세션 거부 */
  const dbE = makeDb();
  const UE = "slow-user";
  const sE = await cert.handleStart(dbE, UE);
  const sidE = sE.body.sid;
  const sessIdE = JSON.parse(b64urlDecode(sidE.slice(0, sidE.lastIndexOf(".")))).sessionId;
  const sessE = dbE._store.get(`certSessions/${sessIdE}`);
  dbE._store.set(`certSessions/${sessIdE}`, { ...sessE, exp: Date.now() - 1000 });
  const e1 = await cert.handleSubmit(dbE, UE, { sid: sidE, answers: sessE.ids.map((q) => byId(q).a) });
  assert.strictEqual(e1.status, 400);
  assert.ok(/만료/.test(e1.body.error), "만료 메시지");
  ok("만료 세션 제출 → 거부");

  /* 13) 문항 버전은 시작 시점에 고정된다 */
  const dbF = makeDb();
  const UF = "ver-user";
  const sF = await cert.handleStart(dbF, UF);
  const sessIdF = JSON.parse(b64urlDecode(sF.body.sid.slice(0, sF.body.sid.lastIndexOf(".")))).sessionId;
  assert.ok(dbF._store.get(`certSessions/${sessIdF}`).examVersion, "세션에 examVersion 저장");
  const rightF = dbF._store.get(`certSessions/${sessIdF}`).ids.map((q) => byId(q).a);
  const f1 = await cert.handleSubmit(dbF, UF, { sid: sF.body.sid, answers: rightF, name: "버전" });
  assert.strictEqual(f1.body.examVersion, dbF._store.get(`certSessions/${sessIdF}`).examVersion, "결과가 고정 버전을 사용");
  ok("문항 버전 시작 시점 고정");

  /* 14) 서명키 동시 최초 생성 → 하나로 수렴
     cert 모듈은 키를 프로세스 메모리에 캐시하므로, 여기서는 모듈을 새로 로드해
     "빈 DB + 여러 요청 동시 진입" 상황을 실제로 재현한다. */
  delete require.cache[require.resolve("./cert")];
  const freshCert = require("./cert");
  const dbG = makeDb();
  await Promise.all([1, 2, 3, 4, 5].map((i) => freshCert.handleStart(dbG, "key-race-" + i)));
  const keyDocs = [...dbG._store.entries()].filter(([k]) => k === "config/certsign");
  assert.strictEqual(keyDocs.length, 1, "서명키 문서는 1개");
  const theKey = keyDocs[0][1].key;
  assert.ok(typeof theKey === "string" && theKey.length >= 32, "키 형식");
  /* 그 키로 발급된 수료증이 나중에도 검증돼야 한다(서로 다른 키로 갈리지 않았음) */
  const sG = await freshCert.handleStart(dbG, "key-race-verify");
  const idsG = JSON.parse(b64urlDecode(sG.body.sid.slice(0, sG.body.sid.lastIndexOf(".")))).ids;
  const g1 = await freshCert.handleSubmit(dbG, "key-race-verify", { sid: sG.body.sid, answers: idsG.map((q) => byId(q).a), name: "키" });
  const gv = await freshCert.handleVerify(dbG, g1.body.certId);
  assert.strictEqual(gv.body.verified, true, "단일 키로 발급·검증 일치");
  ok("서명키 동시 생성 → 단일 키로 수렴 및 검증 일치");

  console.log(`\nALL ${pass} CHECKS PASSED`);
})().catch((e) => {
  console.error("\nFAILED:", e && e.message);
  console.error(e);
  process.exit(1);
});
