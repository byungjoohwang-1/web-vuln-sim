/* WEB-VULN-SIM — 통합 진도·마스터리 엔진 (T1 앵커)
 * 사이트 전 학습 페이지(넘버드 + sim-*)에 주입되어 "탐색/완료/점수"를 기록한다.
 * 저장 키는 wvs_ 접두사 → 기존 Google 로그인 클라우드 동기화가 자동 반영.
 * 방어적: 어떤 테마/페이지에서도 콘솔 에러 0, 기존 UI 비간섭.
 * 공개 API: window.WVSProgress { get, summary, isComplete, markVisited, complete, toggle }
 */
(function () {
  'use strict';
  var KEY = 'wvs_progress';
  var XP_PER = 10; // 항목 최초 완료 시 XP

  function nowTs() { return Date.now(); }
  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; }
    catch (e) { return {}; }
  }
  var SCHEMA = 2;   // 1 = 초기(버전 필드 없음), 2 = v 필드 도입

  /**
   * [G06] 스키마 어댑터.
   * 기존 기록을 지우지 않는다. 모양이 달라졌으면 채워 넣기만 하고, 모르는 필드는 남긴다.
   * 손상된 값(문자열 xp, 배열 아닌 items 등)만 안전한 기본값으로 바꾼다.
   */
  function normalize(o) {
    if (!o || typeof o !== 'object' || Array.isArray(o)) o = {};
    if (!o.items || typeof o.items !== 'object' || Array.isArray(o.items)) o.items = {};
    if (typeof o.xp !== 'number' || !isFinite(o.xp) || o.xp < 0) o.xp = Number(o.xp) > 0 ? Number(o.xp) : 0;
    if (!Array.isArray(o.days)) o.days = [];
    /* 항목별 값이 옛 형태(숫자 하나)로 남아 있어도 버리지 않고 감싼다. */
    for (var k in o.items) {
      var it = o.items[k];
      if (typeof it === 'number') o.items[k] = { v: it };
      else if (!it || typeof it !== 'object') o.items[k] = {};
    }
    if (o.v !== SCHEMA) o.v = SCHEMA;
    return o;
  }
  function today() {
    var d = new Date();
    return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
  }
  function touchDay(s) {
    var t = today();
    if (s.days[s.days.length - 1] !== t) { s.days.push(t); if (s.days.length > 120) s.days = s.days.slice(-120); }
  }
  // 연속 학습일(오늘 또는 어제부터 역순 연속)
  function calcStreak(days) {
    if (!days || !days.length) return 0;
    var set = {}; days.forEach(function (d) { set[d] = 1; });
    var cur = new Date(); var t = today();
    if (!set[t]) { cur.setDate(cur.getDate() - 1); } // 오늘 활동 없으면 어제부터
    var n = 0;
    for (var i = 0; i < 400; i++) {
      var key = cur.getFullYear() + '-' + ('0' + (cur.getMonth() + 1)).slice(-2) + '-' + ('0' + cur.getDate()).slice(-2);
      if (set[key]) { n++; cur.setDate(cur.getDate() - 1); } else break;
    }
    return n;
  }
  function save(o) {
    try { o.updated = nowTs(); localStorage.setItem(KEY, JSON.stringify(o)); }
    catch (e) { /* quota/private mode — 무시 */ }
  }
  function pageId() {
    var p = (location.pathname || '').split('/').pop();
    return p || 'index.html';
  }
  /* 학습 항목(칩 노출 대상) 판별.
     [G02] 예전에는 이 정규식을 손으로 관리해서 카탈로그 생성기와 어긋났다
     (15_privacy 는 카탈로그에 있는데 여기 없어 방문 기록이 안 됐고,
      도구 3종은 여기 있는데 카탈로그에 없어 완료 수와 XP 가 따로 놀았다).
     아래 블록은 _gen/gen_progress_catalog.py 가 같은 정의에서 생성한다. 직접 고치지 말 것. */
  /* <generated:learnable> */
  var LEARNABLE = /^(03_code|04_design|05_linux|06_db|07_fin|07_iss|07_srv|08_win|09_net|10_sec|11_cloud|12_ics|17_fw|13_ai|14_auto|15_privacy|16_zt)/;
  var TOOLS = /^(vulnlab\.html|redteam\.html|quiz-forge\.html|incident\.html|privacy-data-transfer\.html|privacy-rights-desk\.html|privacy-breach-72h\.html|audit-ismsp-lab\.html|industry-tech-protect\.html|ai-grader\.html|lab-generator\.html|skill-assess\.html|fin-eval\.html|mp-assessment\.html|pia-assessment\.html|privacy-breach-drill\.html|privacy-consent-designer\.html|privacy-policy-builder\.html|privacy-policy-eval\.html|privacy-processor-check\.html|privacy-quiz\.html)$/;
  /* </generated:learnable> */
  function isLearnable(id) { return LEARNABLE.test(id) || /^sim-/.test(id) || TOOLS.test(id); }

  var API = {
    get: function () { return normalize(load()); },
    isComplete: function (id) {
      var it = this.get().items[id || pageId()];
      return !!(it && it.c);
    },
    // 마스터리 요약 { visited, completed, xp, level }
    summary: function () {
      var s = this.get(), v = 0, c = 0;
      for (var k in s.items) { if (s.items[k].v) v++; if (s.items[k].c) c++; }
      return { visited: v, completed: c, xp: s.xp, level: Math.floor(Math.sqrt(s.xp / 100)) + 1, streak: calcStreak(s.days) };
    },
    markVisited: function (id) {
      id = id || pageId();
      var s = this.get();
      var newV = !s.items[id] || !s.items[id].v;
      if (!s.items[id]) s.items[id] = {};
      if (newV) s.items[id].v = nowTs();
      var before = s.days.length;
      touchDay(s);
      if (newV || s.days.length !== before) save(s);
      return s.items[id];
    },
    // 완료 처리(선택적 점수 0~100). 최초 1회만 XP 지급.
    complete: function (score, id) {
      id = id || pageId();
      var s = this.get();
      var it = s.items[id] || (s.items[id] = {});
      if (!it.v) it.v = nowTs();
      it.c = nowTs();
      if (typeof score === 'number') it.s = Math.max(0, Math.min(100, Math.round(score)));
      var gained = 0;
      if (!it.x) { it.x = 1; s.xp += XP_PER; gained = XP_PER; } // 최초 완료만 XP
      touchDay(s);
      save(s);
      emit('wvs:progress', { id: id, completed: true, gained: gained, summary: this.summary() });
      return gained;
    },
    // 완료 해제(오클릭 대비). XP는 회수하지 않음(x 플래그 유지 → 재완료 시 중복 지급 방지)
    uncomplete: function (id) {
      id = id || pageId();
      var s = this.get(), it = s.items[id];
      if (it && it.c) { delete it.c; save(s); emit('wvs:progress', { id: id, completed: false, summary: this.summary() }); }
    },
    toggle: function (id) {
      id = id || pageId();
      if (this.isComplete(id)) { this.uncomplete(id); return false; }
      this.complete(undefined, id); return true;
    },
    /* [G06] 내보내기 — 기기 변경·초기화 전에 사용자가 직접 백업할 수 있어야 한다. */
    exportJson: function () {
      return JSON.stringify({ kind: 'wvs-progress-export', v: SCHEMA, exportedAt: new Date().toISOString(), data: this.get() });
    },
    /**
     * 복구. 기본은 병합(merge)이라 기존 기록을 덮어써 잃지 않는다.
     * 같은 항목은 "더 진행된 쪽"을 남긴다(완료 > 방문, 더 늦은 시각).
     * @returns {{ok:boolean, merged:number, error?:string}}
     */
    importJson: function (text, replace) {
      var parsed;
      try { parsed = JSON.parse(text); } catch (e) { return { ok: false, merged: 0, error: 'JSON 형식이 아닙니다.' }; }
      var incoming = normalize(parsed && parsed.data ? parsed.data : parsed);
      if (replace) { save(incoming); return { ok: true, merged: Object.keys(incoming.items).length }; }
      var cur = this.get(), n = 0;
      for (var id in incoming.items) {
        var a = cur.items[id], b = incoming.items[id];
        if (!a) { cur.items[id] = b; n++; continue; }
        if (b.c && !a.c) { a.c = b.c; n++; }
        if (b.v && (!a.v || b.v < a.v)) { a.v = b.v; }      /* 처음 본 시각은 이른 쪽 */
        if (typeof b.s === 'number' && (typeof a.s !== 'number' || b.s > a.s)) a.s = b.s;
        if (b.x) a.x = 1;
      }
      /* XP 는 합산하지 않는다(중복 지급 방지). 완료 수 기준으로 다시 계산한다. */
      var done = 0;
      for (var k2 in cur.items) if (cur.items[k2].x) done++;
      cur.xp = done * XP_PER;
      incoming.days.forEach(function (d) { if (cur.days.indexOf(d) < 0) cur.days.push(d); });
      cur.days.sort();
      save(cur);
      return { ok: true, merged: n };
    },
    schemaVersion: SCHEMA
  };
  function emit(name, detail) {
    try { window.dispatchEvent(new CustomEvent(name, { detail: detail })); } catch (e) {}
  }
  window.WVSProgress = API;

  // ── 플로팅 완료 칩 (학습 페이지에만) ─────────────────────────────
  function injectChip() {
    var id = pageId();
    if (!isLearnable(id)) return;                 // 콘텐츠/실습 페이지만
    if (document.getElementById('wvs-progress-chip')) return;
    if (!document.body) return;

    var wrap = document.createElement('div');
    wrap.id = 'wvs-progress-chip';
    wrap.setAttribute('role', 'group');
    wrap.style.cssText = [
      /* [G05] 예전에는 2147483000 이라 검색 모달 위에 떠서 클릭까지 됐다. 공통 층을 쓴다. */
      'position:fixed', 'left:var(--wvs-edge,14px)', 'bottom:var(--wvs-edge,14px)',
      'z-index:var(--wvs-z-float,300)', 'transition:opacity .15s ease',
      'font-family:system-ui,-apple-system,"Segoe UI","Malgun Gothic",sans-serif',
      'display:flex', 'align-items:center', 'gap:8px'
    ].join(';');

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'wvs-progress-btn';
    btn.style.cssText = [
      'cursor:pointer', 'border:1px solid rgba(148,163,184,.5)',
      'background:rgba(15,23,42,.92)', 'color:#e2e8f0', 'border-radius:999px',
      'padding:9px 15px', 'font-size:13px', 'font-weight:700', 'line-height:1',
      'box-shadow:0 6px 20px rgba(0,0,0,.35)', 'backdrop-filter:blur(6px)',
      'display:inline-flex', 'align-items:center', 'gap:8px', 'transition:transform .12s ease'
    ].join(';');
    btn.addEventListener('mouseenter', function () { btn.style.transform = 'translateY(-2px)'; });
    btn.addEventListener('mouseleave', function () { btn.style.transform = 'none'; });

    function render() {
      var done = API.isComplete(id);
      btn.innerHTML = done
        ? '<span style="color:#22c55e;font-size:15px">✓</span><span data-en="Completed">완료됨</span>'
        : '<span style="width:13px;height:13px;border:2px solid #94a3b8;border-radius:50%;display:inline-block"></span><span data-en="Mark complete">이 항목 완료</span>';
      btn.setAttribute('aria-pressed', done ? 'true' : 'false');
      btn.title = done ? '완료 해제하려면 클릭' : '학습을 완료로 표시';
      // 언어 토글이 있는 페이지면 즉시 반영
      try {
        if (typeof window.isEn === 'function' && window.isEn()) {
          btn.querySelectorAll('[data-en]').forEach(function (el) { el.textContent = el.getAttribute('data-en'); });
        }
      } catch (e) {}
    }
    btn.addEventListener('click', function () {
      var nowDone = API.toggle(id);
      render();
      if (nowDone) flashXp();
    });

    wrap.appendChild(btn);
    document.body.appendChild(wrap);
    render();

    /* 칩은 원래 자기 클릭에만 다시 그렸다. 그래서 페이지 안의 실습이
       complete() 로 완료를 기록해도 새로고침 전까지 '이 항목 완료'로 남아 있었다.
       (07_fincloud, 03_code 의 현업 진단 실습이 모두 이 경로를 쓴다) */
    window.addEventListener('wvs:progress', function (e) {
      if (!e || !e.detail || e.detail.id === id) render();
    });

    function flashXp() {
      var f = document.createElement('div');
      f.textContent = '+' + XP_PER + ' XP';
      f.style.cssText = 'color:#fbbf24;font-weight:800;font-size:13px;font-family:inherit;pointer-events:none;opacity:1;transition:transform .9s ease,opacity .9s ease';
      wrap.appendChild(f);
      requestAnimationFrame(function () { f.style.transform = 'translateY(-16px)'; f.style.opacity = '0'; });
      setTimeout(function () { if (f.parentNode) f.parentNode.removeChild(f); }, 950);
    }
  }

  // 탐색 기록: 이탈 방지 위해 4초 체류 후 visited 표시
  function boot() {
    var id = pageId();
    if (isLearnable(id)) {
      setTimeout(function () { try { API.markVisited(id); } catch (e) {} }, 4000);
    }
    injectChip();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
