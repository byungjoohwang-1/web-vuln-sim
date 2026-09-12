/**
 * WEB-VULN-SIM AI 프록시 (대회 데모용)
 * - POST /aiProxy : AI API 중계. 팀 공유 키(Firestore config 컬렉션) 사용.
 *                   프로바이더는 키 형식으로 자동 판별:
 *                   · sk-ant-…              → Anthropic Messages API
 *                   · <id>.<secret> (Z.ai)  → Z.ai GLM chat completions
 *                   IP별 일일 요청 제한(Firestore 카운터, 기본 12회/일).
 * - GET  /aiProxy : 상태 확인(프론트가 프록시 사용 가능 여부를 탐지하는 용도).
 *
 * 프론트는 BYO 키(사용자 개인 키) 우선 → 프록시 → 데모 AI 순으로 폴백한다.
 * 시크릿 키는 Firestore 콘솔에서 config 컬렉션 내 key 필드로 설정한다
 * (보안 규칙상 클라이언트는 읽을 수 없고 Admin SDK만 접근 가능).
 */
const { onRequest } = require("firebase-functions/v2/https");
const logger = require("firebase-functions/logger");
const crypto = require("crypto");

const admin = require("firebase-admin");
admin.initializeApp();
const db = admin.firestore();

const DAILY_LIMIT = 12;
/* IP당 제한만으로는 청구서를 막지 못한다(IP는 얼마든지 늘어난다).
   전체 호출에 하루 상한을 두어 최악의 경우 비용을 유한하게 만든다.
   상한에 닿으면 프록시는 조용히 거절하고 클라이언트는 BYO 키/데모 계층으로 폴백한다. */
const GLOBAL_DAILY_LIMIT = 1500;
const MAX_TOKENS_CAP = 800;
const MAX_MESSAGES = 14;
const MAX_CHAR_PER_MSG = 4000;

/* 프로바이더별 설정 */
const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const MODEL_ANTHROPIC = "claude-haiku-4-5";
const ALLOWED_ANTHROPIC = new Set([MODEL_ANTHROPIC, "claude-sonnet-4-6"]);

const ZAI_URL = "https://api.z.ai/api/paas/v4/chat/completions";
const ZAI_ANTHROPIC_URL = "https://api.z.ai/api/anthropic/v1/messages";
const MODEL_ZAI = "glm-4.6";
const ALLOWED_ZAI = new Set([MODEL_ZAI, "glm-4.5", "glm-4.5-air", "glm-4.5-flash"]);

const CORS_ORIGINS = new Set([
  "https://vuln-sim.web.app",
  "https://vuln-sim.firebaseapp.com",
  "http://localhost:5000",
  "http://127.0.0.1:5000",
]);

/** 키 형식으로 프로바이더 판별 ("anthropic" | "zai" | "") */
function providerOf(key) {
  if (key.startsWith("sk-ant-")) return "anthropic";
  if (/^[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{4,}$/.test(key)) return "zai";
  return "";
}

function setCors(req, res) {
  const origin = req.headers.origin || "";
  if (CORS_ORIGINS.has(origin)) {
    res.set("Access-Control-Allow-Origin", origin);
    res.set("Vary", "Origin");
    res.set("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
    res.set("Access-Control-Allow-Headers", "Content-Type");
  }
}

function getClientIp(req) {
  const fwd = req.headers["x-forwarded-for"] || "";
  return String(fwd.split(",")[0] || "").trim() || "unknown";
}

/** IP+날짜 조합 카운터. Firestore 장애 시 메모리 폴백(최소 안전장치). */
const memCounter = new Map();
async function rateLimit(ip) {
  const day = new Date().toISOString().slice(0, 10);
  const id = crypto.createHash("sha256").update(`${ip}:${day}`).digest("hex").slice(0, 40);
  const ref = db.collection("rl").doc(id);
  try {
    const n = await db.runTransaction((tx) =>
      tx.get(ref).then((snap) => {
        const cur = snap.exists ? (snap.data().n || 0) : 0;
        if (cur + 1 > DAILY_LIMIT) throw new Error("RATE_LIMITED");
        tx.set(ref, { n: cur + 1, day, ts: admin.firestore.FieldValue.serverTimestamp() }, { merge: true });
        return cur + 1;
      }),
    );
    return { ok: true, n };
  } catch (e) {
    if (e && e.message === "RATE_LIMITED") return { ok: false, reason: "rate" };
    // Firestore 사용 불가 → 메모리 카운터로라도 제한(인스턴스 로컬)
    const cur = (memCounter.get(id) || 0) + 1;
    memCounter.set(id, cur);
    logger.warn("rate-limit firestore fallback", { error: String(e) });
    return cur > DAILY_LIMIT ? { ok: false, reason: "rate" } : { ok: true, n: cur };
  }
}

/**
 * 사이트 전체 일일 호출 상한. IP 단위 제한을 우회하는 분산 남용으로부터
 * 비용을 보호한다. Firestore 를 못 쓰면 인스턴스 로컬 카운터로라도 센다.
 */
async function globalBudget() {
  const day = new Date().toISOString().slice(0, 10);
  const ref = db.collection("rl").doc(`_global:${day}`);
  try {
    const n = await db.runTransaction((tx) =>
      tx.get(ref).then((snap) => {
        const cur = snap.exists ? (snap.data().n || 0) : 0;
        if (cur + 1 > GLOBAL_DAILY_LIMIT) throw new Error("BUDGET");
        tx.set(ref, { n: cur + 1, day, ts: admin.firestore.FieldValue.serverTimestamp() }, { merge: true });
        return cur + 1;
      }),
    );
    return { ok: true, n };
  } catch (e) {
    if (e && e.message === "BUDGET") return { ok: false };
    const k = `_g:${day}`;
    const cur = (memCounter.get(k) || 0) + 1;
    memCounter.set(k, cur);
    logger.warn("global-budget firestore fallback", { error: String(e) });
    return { ok: cur <= GLOBAL_DAILY_LIMIT, n: cur };
  }
}

/**
 * config/anthropic 문서를 우선 읽고, 없으면 config 컬렉션의 어떤 문서에서든
 * key 필드를 찾는다(콘솔에서 문서 ID를 약간 다르게 만들어도 동작하도록).
 */
async function loadApiKey() {
  const snap = await db.collection("config").doc("anthropic").get();
  let key = snap.exists ? snap.data().key : "";
  if (typeof key !== "string" || !key) {
    const qs = await db.collection("config").limit(5).get();
    for (const d of qs.docs) {
      const k = d.data().key;
      if (typeof k === "string" && k) { key = k; break; }
    }
  }
  return key;
}

function validateBody(b) {
  if (!b || typeof b !== "object") return "body 없음";
  if (!Array.isArray(b.messages) || b.messages.length === 0) return "messages 필요";
  if (b.messages.length > MAX_MESSAGES) return `messages 최대 ${MAX_MESSAGES}개`;
  for (const m of b.messages) {
    if (!m || (m.role !== "user" && m.role !== "assistant")) return "role은 user/assistant만";
    if (typeof m.content !== "string" || !m.content.trim()) return "content 필요";
    if (m.content.length > MAX_CHAR_PER_MSG) return `content 최대 ${MAX_CHAR_PER_MSG}자`;
  }
  return null;
}

function upstreamHint(status) {
  return status === 401 ? "공유 키가 유효하지 않습니다(관리자 확인 필요)." :
    status === 403 ? "공유 키에 이 모델 접근 권한이 없습니다." :
    status === 429 ? "공유 키 사용량 한도에 도달했습니다. 잠시 후 다시 시도하거나 내 키를 등록해 주세요." :
    "AI 서버 오류가 발생했습니다.";
}

/** Anthropic Messages API 호출 */
async function callAnthropic(apiKey, payload) {
  const r = await fetch(ANTHROPIC_URL, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify(payload),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    logger.warn("anthropic upstream error", { status: r.status, type: data.error && data.error.type });
    return { status: 502, hint: upstreamHint(r.status) };
  }
  const text = (data.content || []).filter((c) => c.type === "text").map((c) => c.text).join("\n");
  return { text, model: data.model || payload.model, usage: data.usage || null };
}

/** Z.ai — Anthropic 호환 엔드포인트(GLM Coding Plan 구독 쿼터 적용) */
async function callZaiAnthropic(apiKey, payload) {
  // GLM-4.6은 thinking이 기본 활성 → 데모용 응답 속도를 위해 명시적으로 비활성
  const body = { ...payload, thinking: { type: "disabled" } };
  const r = await fetch(ZAI_ANTHROPIC_URL, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify(body),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    return { failed: true, status: r.status, err: (data.error && (data.error.message || data.error.type)) || "" };
  }
  const text = (data.content || []).filter((c) => c.type === "text").map((c) => c.text).join("\n");
  return { text, model: data.model || payload.model, usage: data.usage || null };
}

/** Z.ai — OpenAI 호환 chat completions(표준 API, 종량 과금) */
async function callZaiOpenai(apiKey, payload) {
  const messages = [];
  if (payload.system) messages.push({ role: "system", content: payload.system });
  for (const m of payload.messages) messages.push({ role: m.role, content: m.content });
  const r = await fetch(ZAI_URL, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({ model: payload.model, messages, max_tokens: payload.max_tokens }),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    return { failed: true, status: r.status, err: (data.error && (data.error.message || data.error.code)) || "" };
  }
  const choice = (data.choices || [])[0] || {};
  const text = (choice.message && choice.message.content) || "";
  return { text, model: data.model || payload.model, usage: data.usage || null };
}

/** Z.ai 키 — 구독(Coding Plan) 엔드포인트와 표준 API를 순차 시도. 성공 경로는 인스턴스에 캐시 */
let zaiPref = "";
async function callZai(apiKey, payload) {
  if (zaiPref !== "openai") {
    const a = await callZaiAnthropic(apiKey, payload);
    if (!a.failed) { zaiPref = "anthropic"; return a; }
    logger.warn("zai anthropic-compat failed", { status: a.status, error: a.err });
    if (zaiPref === "anthropic") return zaiFail(a);
  }
  const o = await callZaiOpenai(apiKey, payload);
  if (!o.failed) { zaiPref = "openai"; return o; }
  logger.warn("zai openai-compat failed", { status: o.status, error: o.err });
  return zaiFail(o);
}
function zaiFail(f) {
  if (/insufficient balance|no resource package/i.test(f.err || "")) {
    return { status: 502, hint: "공유 키 잔액/리소스 패키지가 부족합니다(관리자 충전 필요)." };
  }
  return { status: 502, hint: upstreamHint(f.status) };
}

exports.aiProxy = onRequest({ memory: "256MiB", timeoutSeconds: 60, cors: true }, async (req, res) => {
  setCors(req, res);
  if (req.method === "OPTIONS") return res.status(204).send("");
  if (req.method === "GET") {
    return res.status(200).json({ ok: true, service: "wvs-ai-proxy", providers: ["anthropic", "zai"], limit: DAILY_LIMIT });
  }
  if (req.method !== "POST") return res.status(405).json({ ok: false, error: "method" });

  const err = validateBody(req.body);
  if (err) return res.status(400).json({ ok: false, error: err });

  const ip = getClientIp(req);
  const rl = await rateLimit(ip);
  if (!rl.ok) {
    return res.status(429).json({
      ok: false,
      error: "오늘의 무료 체험 횟수를 모두 사용했습니다. 내 API 키를 등록하면 계속 이용할 수 있어요.",
      limit: DAILY_LIMIT,
    });
  }

  /* 사이트 전체 상한 — 분산 남용으로 비용이 무한정 늘어나지 않게 한다. */
  const budget = await globalBudget();
  if (!budget.ok) {
    logger.warn("global daily budget exhausted", { limit: GLOBAL_DAILY_LIMIT });
    return res.status(429).json({
      ok: false,
      error: "오늘 사이트 전체 무료 체험 한도에 도달했습니다. 내 API 키를 등록하면 바로 이용할 수 있어요.",
      scope: "global",
    });
  }

  let apiKey;
  try {
    apiKey = await loadApiKey();
  } catch (e) {
    logger.error("key load fail", { error: String(e) });
    return res.status(503).json({ ok: false, error: "설정 저장소(Firestore)에 연결할 수 없습니다." });
  }
  const provider = providerOf(apiKey || "");
  if (!provider) {
    return res.status(503).json({ ok: false, error: "관리자 API 키가 아직 설정되지 않았거나 형식을 인식할 수 없습니다. (Firestore config 컬렉션의 key 필드)" });
  }

  const allowed = provider === "zai" ? ALLOWED_ZAI : ALLOWED_ANTHROPIC;
  const fallbackModel = provider === "zai" ? MODEL_ZAI : MODEL_ANTHROPIC;
  const model = allowed.has(req.body.model) ? req.body.model : fallbackModel;
  const payload = {
    model,
    max_tokens: Math.min(Number(req.body.max_tokens) || 500, MAX_TOKENS_CAP),
    messages: req.body.messages.map((m) => ({ role: m.role, content: m.content.slice(0, MAX_CHAR_PER_MSG) })),
  };
  if (typeof req.body.system === "string" && req.body.system.trim()) {
    payload.system = req.body.system.slice(0, 2000);
  }

  try {
    const out = provider === "zai"
      ? await callZai(apiKey, payload)
      : await callAnthropic(apiKey, payload);
    if (out.status) return res.status(out.status).json({ ok: false, error: out.hint, upstream: true });
    return res.status(200).json({
      ok: true,
      tier: "proxy",
      model: out.model,
      text: out.text,
      usage: out.usage,
      remaining: DAILY_LIMIT - rl.n,
    });
  } catch (e) {
    logger.error("fetch fail", { provider, error: String(e) });
    return res.status(502).json({ ok: false, error: "AI 서버에 연결할 수 없습니다." });
  }
});

/* ─────────────────────────────────────────────────────────────────────────
 * 검증된 수료증 API (QA-P0-05)
 *   POST /certApi {action:'start'}                        → 서버가 문항 배부(정답 제외) + 서명된 sid
 *   POST /certApi {action:'submit', sid, answers, name}   → 서버 채점 → 합격 시 서명된 수료증 발급
 *   GET  /certApi?action=verify&id=<certId>               → 발급 사실 + 서명 유효성(공개)
 *
 * start/submit 은 Firebase ID 토큰(Authorization: Bearer …)이 필요하다.
 * 발급 문서는 Admin SDK로만 기록하며, 클라이언트 직접 쓰기는 firestore.rules 에서 차단한다.
 * ───────────────────────────────────────────────────────────────────────── */
const certSvc = require("./cert");

async function requireUid(req) {
  const h = String(req.headers.authorization || "");
  const m = /^Bearer\s+(.+)$/i.exec(h);
  if (!m) return null;
  try {
    const decoded = await admin.auth().verifyIdToken(m[1]);
    return decoded && decoded.uid ? decoded.uid : null;
  } catch (e) {
    logger.warn("certApi: invalid id token", { error: String(e) });
    return null;
  }
}

exports.certApi = onRequest({ memory: "256MiB", timeoutSeconds: 60, cors: true }, async (req, res) => {
  try {
    if (req.method === "OPTIONS") return res.status(204).send("");

    // 검증은 공개(로그인 불필요) — 제3자가 수료증 진위를 확인할 수 있어야 한다.
    if (req.method === "GET") {
      const action = String(req.query.action || "");
      if (action === "verify") {
        const id = String(req.query.id || "");
        if (!id) return res.status(400).json({ ok: false, error: "id 필요" });
        const r = await certSvc.handleVerify(db, id);
        return res.status(r.status).json(r.body);
      }
      return res.status(200).json({
        ok: true, service: "wvs-cert-api",
        questionsPerExam: certSvc.QUESTIONS_PER_EXAM,
        passPercent: Math.round(certSvc.PASS_RATIO * 100),
        maxAttemptsPerDay: certSvc.MAX_ATTEMPTS_PER_DAY,
      });
    }

    if (req.method !== "POST") return res.status(405).json({ ok: false, error: "method" });

    const uid = await requireUid(req);
    if (!uid) return res.status(401).json({ ok: false, error: "로그인이 필요합니다(유효한 ID 토큰 없음)." });

    const body = req.body && typeof req.body === "object" ? req.body : {};
    const action = String(body.action || "");
    if (action === "start") {
      const r = await certSvc.handleStart(db, uid);
      return res.status(r.status).json(r.body);
    }
    if (action === "submit") {
      const r = await certSvc.handleSubmit(db, uid, body);
      return res.status(r.status).json(r.body);
    }
    return res.status(400).json({ ok: false, error: "action 은 start|submit 이어야 합니다." });
  } catch (e) {
    logger.error("certApi fail", { error: String(e && e.stack || e) });
    return res.status(500).json({ ok: false, error: "서버 오류" });
  }
});
