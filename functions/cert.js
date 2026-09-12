/**
 * 검증된 수료증(Verified Credential) 발급·검증 — 서버 채점 + HMAC 서명.
 *
 * 배경(QA-P0-05): 기존 수료증은 브라우저의 localStorage 진도만 보고 클라이언트에서 만들어졌고,
 * "해시"는 공개 데이터의 단순 SHA-256이라 서명이 아니었다. 또 Firestore 규칙이 uid 일치만 검사해
 * 누구나 임의 점수·수료증을 직접 기록할 수 있었다.
 *
 * 이 모듈은 다음을 보장한다.
 *  1) 문제와 정답은 서버에만 있다(exam-bank.js). 채점은 전적으로 서버에서 수행한다.
 *  2) 발급 문서는 Admin SDK로만 기록한다. 클라이언트 직접 쓰기는 보안 규칙에서 차단한다.
 *  3) 수료증에는 서버 비밀키 기반 HMAC 서명(sig)이 붙는다. 내용이 바뀌면 서명이 깨진다.
 *  4) 응시 세션(sid)도 서명·만료가 있어 문항 목록이나 uid를 위조할 수 없다.
 *
 * 정답 유출 방지: 매 응시마다 은행에서 무작위 부분집합을 뽑고, 하루 응시 횟수를 제한하며,
 * 불합격 시에는 문항별 정답을 돌려주지 않고 분야별 약점만 알려준다.
 */
const crypto = require("crypto");
const { BANK, publicView, byId, EXAM_VERSION } = require("./exam-bank");

const QUESTIONS_PER_EXAM = 16;
const PASS_RATIO = 0.75;              // 12 / 16
const SID_TTL_MS = 30 * 60 * 1000;    // 응시 세션 30분
const MAX_ATTEMPTS_PER_DAY = 3;

let cachedSecret = null;

/** 서명용 비밀키. config/certsign 문서에 보관(클라이언트는 규칙상 읽을 수 없음). 없으면 생성. */
async function getSecret(db) {
  if (cachedSecret) return cachedSecret;
  const ref = db.collection("config").doc("certsign");
  const snap = await ref.get();
  let key = snap.exists ? snap.data().key : "";
  if (typeof key !== "string" || key.length < 32) {
    key = crypto.randomBytes(32).toString("hex");
    await ref.set({ key, createdAt: new Date().toISOString() }, { merge: true });
  }
  cachedSecret = key;
  return key;
}

function hmac(secret, msg) {
  return crypto.createHmac("sha256", secret).update(msg).digest("hex");
}
function b64url(buf) {
  return Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function unb64url(s) {
  s = String(s).replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  return Buffer.from(s, "base64").toString("utf8");
}
/** 타이밍 안전 비교 */
function safeEq(a, b) {
  const x = Buffer.from(String(a));
  const y = Buffer.from(String(b));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}

/** 수료증 정본 문자열 — 검증 측과 반드시 동일해야 한다. */
function certCanonical(c) {
  return ["WVS-CERT-v2", c.certId, c.uid, c.name, c.score, c.correct, c.total, c.issuedAt, c.examVersion].join("|");
}

function pickQuestions(n) {
  const pool = BANK.slice();
  for (let i = pool.length - 1; i > 0; i--) {
    const j = crypto.randomInt(i + 1);
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool.slice(0, Math.min(n, pool.length));
}

/** 오늘 응시 횟수(uid 기준) */
async function attemptsToday(db, uid) {
  const day = new Date().toISOString().slice(0, 10);
  const ref = db.collection("certAttempts").doc(`${uid}_${day}`);
  const snap = await ref.get();
  return { ref, n: snap.exists ? (snap.data().n || 0) : 0, day };
}

async function handleStart(db, uid) {
  const { ref, n, day } = await attemptsToday(db, uid);
  if (n >= MAX_ATTEMPTS_PER_DAY) {
    return { status: 429, body: { ok: false, error: `하루 응시 횟수(${MAX_ATTEMPTS_PER_DAY}회)를 초과했습니다. 내일 다시 시도해 주세요.` } };
  }
  await ref.set({ n: n + 1, day, uid, updatedAt: new Date().toISOString() }, { merge: true });

  const picked = pickQuestions(QUESTIONS_PER_EXAM);
  const secret = await getSecret(db);
  const payload = { uid, ids: picked.map((q) => q.id), iat: Date.now(), nonce: crypto.randomBytes(8).toString("hex") };
  const body = b64url(JSON.stringify(payload));
  const sid = `${body}.${hmac(secret, body)}`;

  return {
    status: 200,
    body: {
      ok: true, sid, total: picked.length, passRatio: PASS_RATIO, examVersion: EXAM_VERSION,
      attemptsLeft: MAX_ATTEMPTS_PER_DAY - (n + 1),
      questions: picked.map((q, i) => publicView(q, i + 1)),
    },
  };
}

async function handleSubmit(db, uid, bodyIn) {
  const secret = await getSecret(db);
  const sid = String(bodyIn.sid || "");
  const dot = sid.lastIndexOf(".");
  if (dot < 1) return { status: 400, body: { ok: false, error: "응시 세션이 올바르지 않습니다." } };
  const raw = sid.slice(0, dot);
  const sig = sid.slice(dot + 1);
  if (!safeEq(sig, hmac(secret, raw))) {
    return { status: 400, body: { ok: false, error: "응시 세션 서명이 유효하지 않습니다(위조 감지)." } };
  }
  let payload;
  try { payload = JSON.parse(unb64url(raw)); } catch { return { status: 400, body: { ok: false, error: "응시 세션 해독 실패" } }; }
  if (payload.uid !== uid) return { status: 403, body: { ok: false, error: "응시 세션의 사용자와 로그인 사용자가 다릅니다." } };
  if (Date.now() - Number(payload.iat || 0) > SID_TTL_MS) {
    return { status: 400, body: { ok: false, error: "응시 시간이 만료되었습니다. 다시 시작해 주세요." } };
  }

  const ids = Array.isArray(payload.ids) ? payload.ids : [];
  const answers = Array.isArray(bodyIn.answers) ? bodyIn.answers : [];
  if (answers.length !== ids.length) return { status: 400, body: { ok: false, error: "답안 수가 문항 수와 다릅니다." } };

  // ── 서버 채점 (정답은 서버에만 존재) ──
  let correct = 0;
  const weakByCat = {};
  const perQuestion = [];
  ids.forEach((qid, i) => {
    const q = byId(qid);
    if (!q) return;
    const got = Number.isInteger(answers[i]) ? answers[i] : -1;
    const ok = got === q.a;
    if (ok) correct++;
    else weakByCat[q.c] = (weakByCat[q.c] || 0) + 1;
    perQuestion.push({ n: i + 1, id: qid, c: q.c, ok, correctIndex: q.a, e: q.e });
  });

  const total = ids.length;
  const score = total ? Math.round((correct / total) * 100) : 0;
  const pass = total > 0 && correct / total >= PASS_RATIO;

  if (!pass) {
    // 불합격 시 문항별 정답을 돌려주지 않는다(정답 수집 방지). 분야별 약점만 제공.
    return {
      status: 200,
      body: {
        ok: true, pass: false, score, correct, total,
        weakAreas: Object.entries(weakByCat).sort((a, b) => b[1] - a[1]).map(([c, n]) => ({ c, missed: n })),
        message: `합격 기준 ${Math.round(PASS_RATIO * 100)}% 미달입니다. 약점 분야를 학습한 뒤 다시 응시해 주세요.`,
      },
    };
  }

  // ── 합격: 서버가 수료증을 발급하고 서명한다 ──
  const issuedAt = new Date().toISOString();
  const name = String(bodyIn.name || "").trim().slice(0, 40) || "학습자";
  const certId = `WVS-VC-${issuedAt.slice(0, 4)}-${crypto.randomBytes(4).toString("hex").toUpperCase()}`;
  const cert = { certId, uid, name, score, correct, total, issuedAt, examVersion: EXAM_VERSION };
  cert.sig = hmac(secret, certCanonical(cert));

  await db.collection("certificates").doc(certId).set({
    v: 2, kind: "verified", ...cert, createdAt: issuedAt,
  });

  // 리더보드도 서버에서만 기록한다(클라이언트 쓰기는 규칙에서 차단).
  const lbRef = db.collection("leaderboard").doc(uid);
  const prev = await lbRef.get();
  const best = prev.exists ? (prev.data().score || 0) : 0;
  if (score >= best) {
    await lbRef.set({ name, score, certId, examVersion: EXAM_VERSION, verified: true, updatedAt: issuedAt }, { merge: true });
  }

  return {
    status: 200,
    body: {
      ok: true, pass: true, score, correct, total, certId, issuedAt, sig: cert.sig,
      examVersion: EXAM_VERSION,
      review: perQuestion.map((p) => ({ n: p.n, c: p.c, ok: p.ok, e: p.e })),
    },
  };
}

async function handleVerify(db, certId) {
  const snap = await db.collection("certificates").doc(String(certId)).get();
  if (!snap.exists) return { status: 200, body: { ok: true, found: false } };
  const d = snap.data();
  if (d.kind !== "verified" || d.v !== 2) {
    // 구(舊) 클라이언트 발급본 — 서버가 보증하지 않는다.
    return { status: 200, body: { ok: true, found: true, verified: false, legacy: true,
      cert: { certId: d.certId || certId, name: d.name || "", issuedAt: d.date || d.createdAt || "" },
      note: "서버가 발급·서명하지 않은 기록입니다(자가 보고). 공식 검증 대상이 아닙니다." } };
  }
  const secret = await getSecret(db);
  const expect = hmac(secret, certCanonical(d));
  const valid = safeEq(String(d.sig || ""), expect);
  return {
    status: 200,
    body: {
      ok: true, found: true, verified: valid, legacy: false,
      cert: { certId: d.certId, name: d.name, score: d.score, correct: d.correct, total: d.total,
        issuedAt: d.issuedAt, examVersion: d.examVersion },
    },
  };
}

module.exports = { handleStart, handleSubmit, handleVerify, certCanonical, QUESTIONS_PER_EXAM, PASS_RATIO, MAX_ATTEMPTS_PER_DAY };
