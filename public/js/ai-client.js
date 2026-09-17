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

  /* 키 보관 위치.
     이 사이트는 XSS 시뮬레이터를 직접 호스팅하므로, 같은 출처에서 스크립트가 실행되면
     localStorage 의 키를 읽어갈 수 있다. 그래서 기본은 탭을 닫으면 사라지는
     sessionStorage 이고, 사용자가 명시적으로 고를 때만 localStorage 에 남긴다.
     읽을 때는 두 곳을 모두 본다(기존 사용자의 저장분 호환). */
  function readKey(store) {
    try { return (window[store] && window[store].getItem('wvs_ai_key')) || ''; } catch (e) { return ''; }
  }
  function byoKey() { return readKey('sessionStorage') || readKey('localStorage'); }
  function keyScope() { return readKey('sessionStorage') ? 'session' : (readKey('localStorage') ? 'persistent' : 'none'); }
  /** Z.ai(GLM) 키 형식: <id>.<secret> */
  function isZaiKey(k) { return /^[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{4,}$/.test(k || ''); }
  function byoModel() {
    try { var m = localStorage.getItem('wvs_ai_model'); if (m) return m; } catch (e) {}
    return isZaiKey(byoKey()) ? 'glm-4.6' : 'claude-sonnet-4-6';
  }

  function extractJson(text) {
    if (!text) return null;
    /* 옛 구현은 첫 '{' 부터 마지막 '}' 까지 잘라 파싱했다. 실측 평가(P0-1)에서
       GLM 이 닫는 괄호를 하나 더 붙여("}}") 답하는 경우가 관측됐고, 그러면
       파싱이 실패해 좋은 응답이 정적 폴백으로 떨어졌다.
       첫 '{' 에서 시작해 괄호 깊이가 0 이 되는 지점까지(문자열 이스케이프 존중)
       읽는다. 뒤따르는 설명·마크다운 울타리·과잉 괄호에 영향받지 않는다. */
    var s = text.indexOf('{');
    if (s < 0) return null;
    var depth = 0, inStr = false, esc = false;
    for (var i = s; i < text.length; i++) {
      var ch = text.charAt(i);
      if (esc) { esc = false; continue; }
      if (ch === '\\') { esc = true; continue; }
      if (ch === '"') { inStr = !inStr; continue; }
      if (inStr) continue;
      if (ch === '{') depth++;
      else if (ch === '}') {
        depth--;
        if (depth === 0) {
          try { return JSON.parse(text.slice(s, i + 1)); } catch (err) { return null; }
        }
      }
    }
    return null;
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
    /** 키가 어디에 있는지: 'session'(탭 종료 시 소멸) | 'persistent' | 'none' */
    keyScope: keyScope,
    /**
     * @param {string} key
     * @param {string} [model]
     * @param {boolean} [persist=false] true 면 localStorage 에 남긴다(브라우저 재시작 후에도 유지).
     *        기본값 false = sessionStorage. XSS 노출 창을 탭 수명으로 줄이기 위함.
     */
    saveByo: function (key, model, persist) {
      try {
        localStorage.removeItem('wvs_ai_key');
        sessionStorage.removeItem('wvs_ai_key');
        if (key) (persist ? localStorage : sessionStorage).setItem('wvs_ai_key', key);
        if (model) localStorage.setItem('wvs_ai_model', model);
      } catch (e) { /* 프라이빗 모드 등 */ }
    },
    clearByo: function () {
      try { localStorage.removeItem('wvs_ai_key'); sessionStorage.removeItem('wvs_ai_key'); } catch (e) {}
    },
    extractJson: extractJson
  };
})();
