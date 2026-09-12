/**
 * WVS_AI — 3계층 AI 클라이언트 (BYO 키 → 공유 프록시 → 데모 규칙 폴백)
 *
 * 사용:
 *   const r = await WVS_AI.chat({ system, messages, max_tokens });
 *   r.ok && r.tier  // 'byo' | 'proxy'  (실패 시 ok:false → 페이지별 데모 규칙 엔진 사용)
 *   await WVS_AI.probe()  // 프록시 사용 가능 여부 탐지(캐시) → {proxy:boolean}
 *   WVS_AI.tier()   // 현재 예상 계층 'byo' | 'proxy' | 'demo'
 *
 * BYO 키는 기존 AI 코치와 동일한 localStorage 키(wvs_ai_key/wvs_ai_model)를 공유한다.
 */
(function () {
  var PROXY_URL = '/api/ai';
  var PROXY_TIMEOUT = 25000;
  var probeCache = { v: null, ts: 0 };

  function byoKey() { try { return localStorage.getItem('wvs_ai_key') || ''; } catch (e) { return ''; } }
  /** Z.ai(GLM) 키 형식: <id>.<secret> */
  function isZaiKey(k) { return /^[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{4,}$/.test(k || ''); }
  function byoModel() {
    try { var m = localStorage.getItem('wvs_ai_model'); if (m) return m; } catch (e) {}
    return isZaiKey(byoKey()) ? 'glm-4.6' : 'claude-sonnet-4-6';
  }

  function extractJson(text) {
    if (!text) return null;
    var s = text.indexOf('{');
    var e = text.lastIndexOf('}');
    if (s < 0 || e <= s) return null;
    try { return JSON.parse(text.slice(s, e + 1)); } catch (err) { return null; }
  }

  function withTimeout(ms) {
    var c = new AbortController();
    var t = setTimeout(function () { c.abort(); }, ms);
    return { signal: c.signal, clear: function () { clearTimeout(t); } };
  }

  /** 계층 1: BYO — 사용자 개인 키로 직접 호출 (Anthropic 또는 Z.ai GLM) */
  async function chatByo(opts) {
    var key = byoKey();
    if (!key) return { ok: false, tier: 'byo', error: 'no-key' };
    var zai = isZaiKey(key);
    var t = withTimeout(PROXY_TIMEOUT);
    try {
      var r = await fetch(zai ? 'https://api.z.ai/api/anthropic/v1/messages' : 'https://api.anthropic.com/v1/messages', {
        method: 'POST',
        signal: t.signal,
        headers: {
          'content-type': 'application/json',
          'x-api-key': key,
          'anthropic-version': '2023-06-01',
          'anthropic-dangerous-direct-browser-access': 'true'
        },
        body: JSON.stringify({
          model: byoModel(),
          max_tokens: Math.min(opts.max_tokens || 500, 800),
          system: opts.system || undefined,
          messages: opts.messages || [],
          thinking: zai ? { type: 'disabled' } : undefined
        })
      });
      var data = await r.json().catch(function () { return {}; });
      if (!r.ok) {
        var hint = r.status === 401 ? '등록한 API 키가 유효하지 않습니다.' :
          r.status === 429 ? '키 사용량 한도 초과입니다. 잠시 후 시도해 주세요.' :
          'AI 요청 실패 (' + r.status + ')';
        return { ok: false, tier: 'byo', error: hint };
      }
      var text = (data.content || []).filter(function (c) { return c.type === 'text'; })
        .map(function (c) { return c.text; }).join('\n');
      return { ok: true, tier: 'byo', model: byoModel(), text: text, json: extractJson(text) };
    } catch (e) {
      return { ok: false, tier: 'byo', error: e.name === 'AbortError' ? '시간 초과' : '네트워크 오류' };
    } finally { t.clear(); }
  }

  /** 계층 2: 공유 프록시 — 팀 키, IP당 일일 제한 */
  async function chatProxy(opts) {
    var t = withTimeout(PROXY_TIMEOUT);
    try {
      var r = await fetch(PROXY_URL, {
        method: 'POST',
        signal: t.signal,
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          messages: opts.messages || [],
          system: opts.system || '',
          max_tokens: opts.max_tokens || 500,
          model: 'claude-haiku-4-5'
        })
      });
      var data = await r.json().catch(function () { return {}; });
      if (!r.ok || !data.ok) {
        return { ok: false, tier: 'proxy', error: (data && data.error) || ('프록시 오류 ' + r.status), remaining: data && data.remaining };
      }
      return { ok: true, tier: 'proxy', model: data.model, text: data.text, json: extractJson(data.text), remaining: data.remaining };
    } catch (e) {
      return { ok: false, tier: 'proxy', error: e.name === 'AbortError' ? '시간 초과' : '프록시 연결 불가' };
    } finally { t.clear(); }
  }

  window.WVS_AI = {
    /** 통합 호출: BYO → 프록시. 둘 다 실패하면 ok:false (페이지가 데모 규칙 엔진으로 폴백) */
    chat: async function (opts) {
      var r1 = await chatByo(opts);
      if (r1.ok) return r1;
      var r2 = await chatProxy(opts);
      if (r2.ok) return r2;
      return { ok: false, tier: 'none', byoError: r1.error, proxyError: r2.error };
    },
    /** 프록시 생존 탐지(GET, 60초 캐시) */
    probe: async function () {
      var now = Date.now();
      if (probeCache.v !== null && now - probeCache.ts < 60000) return probeCache.v;
      var v = false;
      try {
        var t = withTimeout(6000);
        var r = await fetch(PROXY_URL, { method: 'GET', signal: t.signal });
        var d = await r.json().catch(function () { return {}; });
        v = !!(r.ok && d.ok);
        t.clear();
      } catch (e) { v = false; }
      probeCache = { v: v, ts: now };
      return v;
    },
    /** 현재 사용하게 될 계층 라벨 */
    tier: async function () {
      if (byoKey()) return 'byo';
      var p = await this.probe();
      return p ? 'proxy' : 'demo';
    },
    hasByo: function () { return !!byoKey(); },
    saveByo: function (key, model) {
      try {
        if (key) localStorage.setItem('wvs_ai_key', key); else localStorage.removeItem('wvs_ai_key');
        if (model) localStorage.setItem('wvs_ai_model', model);
      } catch (e) { /* 프라이빗 모드 등 */ }
    },
    extractJson: extractJson
  };
})();
