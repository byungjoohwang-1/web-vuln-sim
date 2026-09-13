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

/**
 * 서명용 비밀키. config/certsign 문서에 보관(클라이언트는 규칙상 읽을 수 없음).
 *
 * [G01] 예전에는 get → 없으면 생성 → set 이라, 여러 인스턴스가 동시에 최초 접근하면
 * 서로 다른 키를 만들어 캐시할 수 있었다(한쪽이 발급한 수료증을 다른 쪽이 위조로 판정).
 * 트랜잭션 안에서 "없을 때만 생성"하면 경쟁하는 쪽은 재시도하며 기존 키를 읽는다.
 */
async function getSecret(db) {
  if (cachedSecret) return cachedSecret;
  const ref = db.collection("config").doc("certsign");
  const key = await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    const cur = snap.exists ? snap.data() : null;
    if (cur && typeof cur.key === "string" && cur.key.length >= 32) return cur.key;
    const fresh = crypto.randomBytes(32).toString("hex");
    tx.set(ref, { key: fresh, kid: crypto.randomBytes(4).toString("hex"), createdAt: new Date().toISOString() }, { merge: true });
    return fresh;
  });
  cachedSecret = key;
  return key;
}

/** 제출 답안의 지문 — 같은 답안 재전송(네트워크 재시도)과 답안 교체를 구분한다. */
function answersFingerprint(ids, answers) {
  return crypto.createHash("sha256")
    .update(JSON.stringify({ ids, answers: answers.map((a) => (Number.isInteger(a) ? a : null)) }))
    .digest("hex");
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

/**
 * 응시 시작.
 *
 * [G01] 예전에는 횟수 조회와 증가가 분리돼 있어(get → set) 동시에 5번 시작해도 전부 통과하고
 * 카운터는 1만 남았다. 횟수 차감과 세션 생성을 한 트랜잭션으로 묶어 원자적으로 처리한다.
 * 세션은 서버 문서로 남겨야 제출 시 "이미 소비된 세션"을 판별할 수 있다(sid 서명만으로는 불가능).
 */
async function handleStart(db, uid) {
  const day = new Date().toISOString().slice(0, 10);
  const counterRef = db.collection("certAttempts").doc(`${uid}_${day}`);
  const picked = pickQuestions(QUESTIONS_PER_EXAM);
  const sessionId = crypto.randomBytes(16).toString("hex");
  const now = Date.now();

  const outcome = await db.runTransaction(async (tx) => {
    const snap = await tx.get(counterRef);
    const n = snap.exists ? (snap.data().n || 0) : 0;
    if (n >= MAX_ATTEMPTS_PER_DAY) return { limited: true, n };
    tx.set(counterRef, { n: n + 1, day, uid, updatedAt: new Date().toISOString() }, { merge: true });
    tx.set(db.collection("certSessions").doc(sessionId), {
      uid,
      ids: picked.map((q) => q.id),
      examVersion: EXAM_VERSION,       // 문항 버전은 시작 시점에 고정한다
      iat: now,
      exp: now + SID_TTL_MS,
      status: "open",
      createdAt: new Date().toISOString(),
    });
    return { limited: false, n: n + 1 };
  });

  if (outcome.limited) {
    return { status: 429, body: { ok: false, error: `하루 응시 횟수(${MAX_ATTEMPTS_PER_DAY}회)를 초과했습니다. 내일 다시 시도해 주세요.` } };
  }

  const secret = await getSecret(db);
  const payload = { sessionId, uid, ids: picked.map((q) => q.id), iat: now, examVersion: EXAM_VERSION };
  const body = b64url(JSON.stringify(payload));
  const sid = `${body}.${hmac(secret, body)}`;

  return {
    status: 200,
    body: {
      ok: true, sid, total: picked.length, passRatio: PASS_RATIO, examVersion: EXAM_VERSION,
      attemptsLeft: Math.max(0, MAX_ATTEMPTS_PER_DAY - outcome.n),
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

  const sessionId = String(payload.sessionId || "");
  if (!sessionId) return { status: 400, body: { ok: false, error: "응시 세션 식별자가 없습니다. 다시 시작해 주세요." } };

  const ids = Array.isArray(payload.ids) ? payload.ids : [];
  const answers = Array.isArray(bodyIn.answers) ? bodyIn.answers : [];
  if (answers.length !== ids.length) return { status: 400, body: { ok: false, error: "답안 수가 문항 수와 다릅니다." } };

  // ── 채점은 순수 계산이므로 트랜잭션 밖에서 미리 한다(정답은 서버에만 존재) ──
  const grade = (qids) => {
    let correct = 0;
    const weakByCat = {};
    const perQuestion = [];
    qids.forEach((qid, i) => {
      const q = byId(qid);
      if (!q) return;
      const got = Number.isInteger(answers[i]) ? answers[i] : -1;
      const isOk = got === q.a;
      if (isOk) correct++;
      else weakByCat[q.c] = (weakByCat[q.c] || 0) + 1;
      perQuestion.push({ n: i + 1, id: qid, c: q.c, ok: isOk, e: q.e });
    });
    const total = qids.length;
    return {
      correct, total,
      score: total ? Math.round((correct / total) * 100) : 0,
      pass: total > 0 && correct / total >= PASS_RATIO,
      weakAreas: Object.entries(weakByCat).sort((a, b) => b[1] - a[1]).map(([c, n]) => ({ c, missed: n })),
      review: perQuestion.map((p) => ({ n: p.n, c: p.c, ok: p.ok, e: p.e })),
    };
  };

  const name = String(bodyIn.name || "").trim().slice(0, 40) || "학습자";
  const issuedAt = new Date().toISOString();
  /* certId 는 세션에서 결정적으로 파생한다 — 부분 실패 후 재시도해도 같은 문서를 쓴다. */
  const certId = `WVS-VC-${issuedAt.slice(0, 4)}-${crypto.createHash("sha256").update("cert:" + sessionId).digest("hex").slice(0, 8).toUpperCase()}`;

  const sessRef = db.collection("certSessions").doc(sessionId);
  const lbRef = db.collection("leaderboard").doc(uid);

  /**
   * [G01] 세션 1회 소비 + 결과 기록 + 수료증 발급 + 리더보드 갱신을 한 트랜잭션에서 처리한다.
   *  - 같은 답안 재전송(네트워크 재시도) → 저장된 결과를 그대로 돌려준다(중복 발급 없음).
   *  - 답안을 바꿔 재제출        → 거부한다(불합격 후 정답 맞춰 재시도 차단).
   * 트랜잭션 규칙상 읽기를 모두 먼저 수행한다.
   */
  const out = await db.runTransaction(async (tx) => {
    const snap = await tx.get(sessRef);
    if (!snap.exists) return { status: 400, body: { ok: false, error: "응시 세션을 찾을 수 없습니다. 다시 시작해 주세요." } };
    const sess = snap.data();
    if (sess.uid !== uid) return { status: 403, body: { ok: false, error: "응시 세션의 사용자와 로그인 사용자가 다릅니다." } };
    if (Date.now() > Number(sess.exp || 0)) return { status: 400, body: { ok: false, error: "응시 시간이 만료되었습니다. 다시 시작해 주세요." } };

    /* 채점 기준은 서버 세션에 고정된 문항·버전을 쓴다(sid 내용이 아니라). */
    const sessIds = Array.isArray(sess.ids) ? sess.ids : [];
    if (sessIds.length !== answers.length) {
      return { status: 400, body: { ok: false, error: "답안 수가 문항 수와 다릅니다." } };
    }
    const fp = answersFingerprint(sessIds, answers);

    if (sess.status === "submitted") {
      if (sess.answersFp === fp && sess.result) {
        return { status: 200, body: { ...sess.result, replayed: true } };   // 동일 재전송 → 결과 복구
      }
      return { status: 409, body: { ok: false, error: "이미 제출한 응시입니다. 답안을 바꿔 다시 제출할 수 없습니다." } };
    }

    const g = grade(sessIds);
    const lbSnap = g.pass ? await tx.get(lbRef) : null;   /* 읽기는 쓰기보다 먼저 */

    const result = g.pass
      ? { ok: true, pass: true, score: g.score, correct: g.correct, total: g.total,
          certId, issuedAt, examVersion: sess.examVersion || EXAM_VERSION, review: g.review }
      : { ok: true, pass: false, score: g.score, correct: g.correct, total: g.total,
          weakAreas: g.weakAreas,
          message: `합격 기준 ${Math.round(PASS_RATIO * 100)}% 미달입니다. 약점 분야를 학습한 뒤 다시 응시해 주세요.` };

    if (g.pass) {
      const cert = { certId, uid, name, score: g.score, correct: g.correct, total: g.total,
        issuedAt, examVersion: sess.examVersion || EXAM_VERSION };
      cert.sig = hmac(secret, certCanonical(cert));
      result.sig = cert.sig;
      tx.set(db.collection("certificates").doc(certId), { v: 2, kind: "verified", ...cert, sessionId, createdAt: issuedAt });
      const best = lbSnap && lbSnap.exists ? (lbSnap.data().score || 0) : 0;
      if (g.score >= best) {
        tx.set(lbRef, { name, score: g.score, certId, examVersion: cert.examVersion, verified: true, updatedAt: issuedAt }, { merge: true });
      }
    }

    /* 합격·불합격 모두 세션을 소비한다. */
    tx.set(sessRef, { status: "submitted", answersFp: fp, result, submittedAt: issuedAt }, { merge: true });
    return { status: 200, body: result };
  });

  return out;
}

/**
 * 검증 응답에 실명을 그대로 싣지 않는다 (QA N-04).
 *
 * 검증은 로그인 없이 열려 있어야 한다(제3자가 수료증 진위를 확인해야 하므로).
 * 그런데 응답에 실명이 그대로 들어가면, 수료번호를 훑는 것만으로 이름을 모을 수 있다.
 * 검증에 필요한 것은 "이 번호의 주인이 내가 받은 증서의 그 사람인가"를 대조하는 것뿐이라
 * 일부를 가려도 목적을 해치지 않는다.
 */
function maskName(raw) {
  const s = String(raw || "").trim();
  if (!s) return "";
  // 공백이 있으면 토큰별로 첫 글자만 남긴다(영문 이름 등): "Hong Gildong" → "H* G*"
  if (/\s/.test(s)) {
    return s.split(/\s+/).filter(Boolean).map((t) => t[0] + "*").join(" ");
  }
  const ch = Array.from(s);                 // 서러게이트 쌍 안전
  if (ch.length <= 1) return "*";
  if (ch.length === 2) return ch[0] + "*";
  return ch[0] + "*".repeat(ch.length - 2) + ch[ch.length - 1];
}

async function handleVerify(db, certId) {
  const snap = await db.collection("certificates").doc(String(certId)).get();
  if (!snap.exists) return { status: 200, body: { ok: true, found: false } };
  const d = snap.data();
  if (d.kind !== "verified" || d.v !== 2) {
    // 구(舊) 클라이언트 발급본 — 서버가 보증하지 않는다.
    return { status: 200, body: { ok: true, found: true, verified: false, legacy: true,
      cert: { certId: d.certId || certId, name: maskName(d.name), issuedAt: d.date || d.createdAt || "" },
      note: "서버가 발급·서명하지 않은 기록입니다(자가 보고). 공식 검증 대상이 아닙니다." } };
  }
  const secret = await getSecret(db);
  const expect = hmac(secret, certCanonical(d));
  const valid = safeEq(String(d.sig || ""), expect);
  return {
    status: 200,
    body: {
      ok: true, found: true, verified: valid, legacy: false,
      cert: { certId: d.certId, name: maskName(d.name), score: d.score, correct: d.correct, total: d.total,
        issuedAt: d.issuedAt, examVersion: d.examVersion },
    },
  };
}

module.exports = { handleStart, handleSubmit, handleVerify, maskName, certCanonical, QUESTIONS_PER_EXAM, PASS_RATIO, MAX_ATTEMPTS_PER_DAY };
